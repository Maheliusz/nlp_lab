import argparse

import numpy as np
import sentencepiece as spm
from fastai.text import torch, MultiBatchRNN, to_gpu, SequentialRNN, LinearDecoder, load_model, no_grad_context, \
    DataLoader, SortSampler, Dataset

parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to root of all res', required=True)
parser.add_argument('--save_to_file', help='Should the scores of n-grams be saved to file "scores.txt"', required=False,
                    action="store_true")

args = parser.parse_args()

# state = torch.load(args.path + 'work/up_low50k/models/fwd_v50k_finetune_lm_enc.h5')

spm_processor = spm.SentencePieceProcessor()
spm_processor.Load(args.path + 'work/up_low50k/tmp/sp-50k.model')

# spm_processor.LoadVocabulary(args.path + 'work/up_low50k/tmp/sp-50k.vocab', threshold=100)

torch.cuda.set_device(0)

UNK_ID = 0
PAD_ID = 1
BOS_ID = 2
EOS_ID = 3
UP_ID = 4
bs = 22

em_sz, nh, nl = 400, 1150, 4

bptt = 5
vs = len(spm_processor)

rnn_enc = MultiBatchRNN(bptt, 1000000, vs, em_sz, nh, nl, pad_token=PAD_ID, bidir=False, qrnn=False)
enc = rnn_enc.encoder
lm = SequentialRNN(rnn_enc, LinearDecoder(vs, em_sz, 0, tie_encoder=enc))

lm = to_gpu(lm)  # for people with gpu
load_model(lm[0], args.path + 'work/up_low50k/models/fwd_v50k_finetune_lm_enc.h5')
lm.reset()
lm.eval()


class LMTextDataset(Dataset):
    def __init__(self, x):
        self.x = x

    def __getitem__(self, idx):
        sentence = self.x[idx]
        return sentence[:-1], sentence[1:]

    def __len__(self):
        return len(self.x)


def next_tokens(ids_, model, deterministic=False):
    ids = [np.array(ids_)]
    test_ds = LMTextDataset(ids)
    test_samp = SortSampler(ids, key=lambda x: len(ids[x]))
    dl = DataLoader(test_ds,
                    bs,
                    transpose=True,
                    transpose_y=True,
                    num_workers=1,
                    pad_idx=PAD_ID,
                    sampler=test_samp,
                    pre_pad=False)

    tensor1 = None
    with no_grad_context():
        for (x, _) in dl:
            tensor1 = model(x)
    p = tensor1[0]

    arg = p[-1]
    r = int(torch.argmax(arg) if deterministic
            else torch.multinomial(p[-1].exp(), 1))  # probability is in logharitm

    while r in [ids_[-1]]:  # , BOS_ID,EOS_ID, UNK_ID]:
        arg[r] = -1
        r = int(torch.argmax(arg))

    predicted_ids = [r]
    return predicted_ids


def next_words_best(ss, model, n_words, deterministic=True):
    ss_ids = spm_processor.encode_as_ids(ss)
    wip = ss
    wip_ids = ss_ids
    for i in range(n_words):
        next_ = next_tokens(wip_ids, model, deterministic)
        wip_ids = wip_ids + next_
        wip = spm_processor.decode_ids(wip_ids)
        wip_ids = spm_processor.encode_as_ids(wip)

    return wip


sentences = [
    "Warszawa to największe", "Te zabawki należą do",
    "Policjant przygląda się", "Na środku skrzyżowania widać",
    "Właściciel samochodu widział złodzieja z",
    "Prezydent z premierem rozmawiali wczoraj o", "Witaj drogi",
    "Gdybym wiedział wtedy dokładnie to co wiem teraz, to bym się nie",
    "Gdybym wiedziała wtedy dokładnie to co wiem teraz, to bym się nie",
    "Polscy naukowcy odkryli w Tatrach nowy gatunek istoty żywej. Zwięrzę to przypomina małpę, lecz porusza się na "
    "dwóch nogach i potrafi posługiwać się narzędziami. Przy dłuższej obserwacji okazało się, że potrafi również "
    "posługiwać się językiem polskim, a konkretnie gwarą podhalańską. Zwierzę to zostało nazwane "
]


def deterministic(sentence: str, n_words=70):
    return next_words_best(sentence, lm, n_words, deterministic=True)


def nondeterministic(sentence: str, n_words=70):
    return next_words_best(sentence, lm, n_words, deterministic=False)


file = open('result.txt', 'w', encoding='utf-8') if args.save_to_file else None

for sentence in sentences:
    det = deterministic(sentence)
    ndet = nondeterministic(sentence)
    print(sentence)
    print("Det:\t" + det)
    print("N-Det:\t" + ndet)
    if args.save_to_file:
        file.write(sentence + '\nDet:\t' + det + '\nN-Det:\t' + ndet + '\n')

if args.save_to_file:
    file.close()
