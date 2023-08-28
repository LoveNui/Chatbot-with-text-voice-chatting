
import numpy as np
import torch
import torchaudio
from encodec import EncodecModel
from encodec.utils import convert_audio
from src.text2speech.hubert.hubert_manager import HuBERTManager
from src.text2speech.hubert.pre_kmeans_hubert import CustomHubert
from src.text2speech.hubert.customtokenizer import CustomTokenizer
from argparse import ArgumentParser

use_large_quant_model = True

def voice_cloning(
        cloned_speaker_name,
        voice_source,
        use_large_quant_model=True, 
        large_model='quantifier_V1_hubert_base_ls960_23.pth', 
        large_tokenizer = 'tokenizer_large.pth',
        base_model='quantifier_hubert_base_ls960_14.pth',
        base_tokenizer='tokenizer.pth',
        device='cuda',
        ):
    
    if use_large_quant_model:
        model = (large_model, large_tokenizer)
    else:
        model = (base_model, base_tokenizer)
    print('Loading HuBERT...')
    hubert_model = CustomHubert(HuBERTManager.make_sure_hubert_installed(), device=device)
    print('Loading Quantizer...')
    quant_model = CustomTokenizer.load_from_checkpoint(HuBERTManager.make_sure_tokenizer_installed(model=model[0], local_file=model[1]), device)
    print('Loading Encodec...')
    encodec_model = EncodecModel.encodec_model_24khz()
    encodec_model.set_target_bandwidth(6.0)
    encodec_model.to(device)
    print('Downloaded and loaded models!')

    # out_file = f'../../customer_files/customer_npz/{cloned_speaker_name}.npz'
    out_file = f'/kaggle/working/AI-avatar-generator/customer_files/customer_npz/{cloned_speaker_name}.npz'
    wav, sr = torchaudio.load(voice_source)

    wav_hubert = wav.to(device)

    if wav_hubert.shape[0] == 2:  # Stereo to mono if needed
        wav_hubert = wav_hubert.mean(0, keepdim=True)

    print('Extracting semantics...')
    semantic_vectors = hubert_model.forward(wav_hubert, input_sample_hz=sr)
    print('Tokenizing semantics...')
    semantic_tokens = quant_model.get_token(semantic_vectors)
    print('Creating coarse and fine prompts...')
    wav = convert_audio(wav, sr, encodec_model.sample_rate, 1).unsqueeze(0)

    wav = wav.to(device)

    with torch.no_grad():
        encoded_frames = encodec_model.encode(wav)
    codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()

    codes = codes.cpu()
    semantic_tokens = semantic_tokens.cpu()

    np.savez(out_file,
            semantic_prompt=semantic_tokens,
            fine_prompt=codes,
            coarse_prompt=codes[:2, :]
            )
    print(f'Save npz to {out_file}')

if __name__ == '__main__':
    parser = ArgumentParser()  
    parser.add_argument("--cloned_speaker_name", default='Hello, I am Dalia', help="text that needs to be converted to the speech")
    parser.add_argument("--voice_source", default='en_speaker_2', help="voice that is used to generate speech")
    args = parser.parse_args()

    voice_cloning("lary", "/kaggle/working/AI-avatar-generator/customer_files/customer_audio_source/lary.wav")