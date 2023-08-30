from deepgram import Deepgram
from inference import video_geneartor
from argparse import ArgumentParser
from bot_src.private_env import DG_KEY
import json
import os

dg = Deepgram(DG_KEY)

params = {
    "punctuate": True,
    "model": 'general',
    "tier": 'nova',
    # 'api_key': dg_key
    }

def speech_to_text(id):
    # Save the file to disk
    speech_file = f'/kaggle/working/AI-avatar-generator/voice_message/{id}.mp3'
    with open(speech_file, "rb") as f:
        source = {"buffer": f, "mimetype": 'audio/' + "mp3"}
        res = dg.transcription.sync_prerecorded(source, params)
        with open("1.json", "w") as transcript:
            json.dump(res, transcript)
    data = json.load(open('1.json'))
    return data["results"]["channels"][0]["alternatives"][0]["transcript"]

def set_parameter():
    parser = ArgumentParser()  
    parser.add_argument("--text", default='Hello, I am Dalia', help="text that needs to be converted to the speech")
    parser.add_argument("--npz", default='en_speaker_2', help="voice that is used to generate speech")
    parser.add_argument("--id", default='default', help="voice that is used to generate speech")
    parser.add_argument("--picture", default='default', help="picture that is used to generate video")
    parser.add_argument("--ref_eyeblink", default=None, help="path to reference video providing eye blinking")
    parser.add_argument("--ref_pose", default=None, help="path to reference video providing pose")
    parser.add_argument("--checkpoint_dir", default='/kaggle/working/AI-avatar-generator/checkpoints', help="path to output")
    parser.add_argument("--result_dir", default='/kaggle/working/AI-avatar-generator/results', help="path to output")
    parser.add_argument("--pose_style", type=int, default=0,  help="input pose style from [0, 46)")
    parser.add_argument("--batch_size", type=int, default=2,  help="the batch size of facerender")
    parser.add_argument("--size", type=int, default=256,  help="the image size of the facerender")
    parser.add_argument("--expression_scale", type=float, default=1.,  help="the batch size of facerender")
    parser.add_argument('--input_yaw', nargs='+', type=int, default=None, help="the input yaw degree of the user ")
    parser.add_argument('--input_pitch', nargs='+', type=int, default=None, help="the input pitch degree of the user")
    parser.add_argument('--input_roll', nargs='+', type=int, default=None, help="the input roll degree of the user")
    parser.add_argument('--enhancer',  type=str, default=None, help="Face enhancer, [gfpgan, RestoreFormer]")
    parser.add_argument('--background_enhancer',  type=str, default=None, help="background enhancer, [realesrgan]")
    # parser.add_argument("--cpu", dest="cpu", action="store_true") 
    parser.add_argument("--face3dvis", action="store_true", help="generate 3d face and 3d landmarks") 
    parser.add_argument("--still", action="store_true", help="can crop back to the original videos for the full body aniamtion") 
    parser.add_argument("--preprocess", default='crop', choices=['crop', 'extcrop', 'resize', 'full', 'extfull'], help="how to preprocess the images" ) 
    parser.add_argument("--verbose",action="store_true", help="saving the intermedia output or not" ) 
    parser.add_argument("--old_version",action="store_true", help="use the pth other than safetensor version" ) 


    # net structure and parameters
    parser.add_argument('--net_recon', type=str, default='resnet50', choices=['resnet18', 'resnet34', 'resnet50'], help='useless')
    parser.add_argument('--init_path', type=str, default=None, help='Useless')
    parser.add_argument('--use_last_fc',default=False, help='zero initialize the last fc')
    parser.add_argument('--bfm_folder', type=str, default='/kaggle/working/AI-avatar-generator/checkpoints/BFM_Fitting/')
    parser.add_argument('--bfm_model', type=str, default='BFM_model_front.mat', help='bfm model')

    # default renderer parameters
    parser.add_argument('--focal', type=float, default=1015.)
    parser.add_argument('--center', type=float, default=112.)
    parser.add_argument('--camera_d', type=float, default=10.)
    parser.add_argument('--z_near', type=float, default=5.)
    parser.add_argument('--z_far', type=float, default=15.)

    args = parser.parse_args()
    return args

def video_response(text, id):
    args = set_parameter()
    args.text = text
    picture_path = f'/kaggle/working/AI-avatar-generator/customer_files/customer_picture/{id}.png'
    if not os.path.exists(picture_path):
        picture_path = '/kaggle/working/AI-avatar-generator/customer_files/customer_picture/default.png'
    args.picture = picture_path
    audio_npz_path =f'/kaggle/working/AI-avatar-generator/customer_files/customer_npz/{id}.npz'
    if not os.path.exists(audio_npz_path):
        audio_npz_path = 'en_speaker_4'
    args.npz = audio_npz_path
    args.id = id
    result_path = video_geneartor(args)
    return result_path + '.mp4'
    