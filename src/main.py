from src.model.flan import FlanInferencer
from src.model.bloomhub import BloomHubInferencer
from src.model.openai import OpenAIGPTInferencer
from src.model.opt import OPTInferencer
from src.datautils import OP_FOLDER_DIR, FinalPromptBuilder
from transformers import T5Tokenizer, T5ForConditionalGeneration
import argparse
import logging
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser()
parser.add_argument( '-log',
                     '--loglevel',
                     default='warning',
                     help='Provide logging level. Example --loglevel debug, default=warning' )
parser.add_argument("--model_name", type=str, default="google/flan-t5-small")
parser.add_argument("--model_path", type=str, default="google/flan-t5-small")
parser.add_argument('-test', action='store_true')
# main function.
if __name__ == "__main__":
    # test and example usage.
    args = parser.parse_args()

    logging.basicConfig( level=args.loglevel.upper() )
    logging.info( 'Logging now setup.' )
    print(args.model_name.lower())
    if 'flan' in args.model_name.lower():
        inferencer = FlanInferencer(args.model_path)
    elif 'gpt' in args.model_name.lower():
        inferencer = OpenAIGPTInferencer(args.model_name, args.model_path)
    elif 'bloomhub' in args.model_name.lower():
        inferencer = BloomHubInferencer(args.model_path)
    elif 'opt' in args.model_name.lower():
        inferencer = OPTInferencer(args.model_path)
    builder = FinalPromptBuilder()
    if args.test:
        test_list_of_prompts = builder.get_test_list_of_prompts(
            inferencer.model_name.split('-')[0]
        )
        inferencer.run(test_list_of_prompts)
    else:
        final_list_of_prompts = builder.get_final_list_of_prompts(
            inferencer.model_name.split('-')[0]
        )
        inferencer.run(final_list_of_prompts)
