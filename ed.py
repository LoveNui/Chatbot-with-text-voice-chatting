from argparse import ArgumentParser

def user(args):
    print(args.text)

def parameter(q):
    parser = ArgumentParser()
    parser.add_argument("--text", default = q, help="text that needs to be converted to the speech")
    parser.add_argument("--speaker", default='en_speaker_2', help="voice that is used to generate speech")
    parser.add_argument("--ref_eyeblink", default=None, help="path to reference video providing eye blinking")
    
    args = parser.parse_args()
    args.text ="hello2"
    return args

if __name__ == '__main__':

    user(parameter("hello"))
