from transformers import AutoProcessor, Idefics3ForConditionalGeneration, StoppingCriteria, StoppingCriteriaList
from PIL import Image
import torch

class EOSCriteria(StoppingCriteria):
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        return input_ids[0][-1] == self.eos_token_id

def main():
    # Load model and processor
    model = Idefics3ForConditionalGeneration.from_pretrained(
        "HuggingFaceTB/SmolVLM-500M-Instruct",
        torch_dtype=torch.float32
    )
    processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-500M-Instruct")
    
    # Initialize stopping criteria
    eos_criteria = EOSCriteria()
    eos_criteria.eos_token_id = processor.tokenizer.eos_token_id

    # Get inputs
    image_path = input("Enter image path: ")
    question = input("Your question: ")

    try:
        image = Image.open(image_path).convert('RGB')
        prompt = f"<image>Question: {question} Answer:"
        
        inputs = processor(
            text=prompt,
            images=image,
            return_tensors="pt",
            padding=True
        )

        outputs = model.generate(
            **inputs,
            max_new_tokens=1,
            do_sample=False,
            stopping_criteria=StoppingCriteriaList([eos_criteria])
        )

        full_response = processor.batch_decode(outputs, skip_special_tokens=True)[0]
        answer = full_response.split("Answer:")[-1].split("Question:")[0].strip()
        
        print(f"\nAnswer: {answer}")

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()