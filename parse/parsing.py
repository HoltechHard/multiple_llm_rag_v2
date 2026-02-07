import re

class LLMParser:        

    def __init__(self):
        self.THINK_PATTERN = re.compile(
            r'<think>(.*?)</think>',
            re.DOTALL | re.IGNORECASE
        )
    
    def parse_llm_response(self, text: str):
        """
        Separates <think>...</think> content (reasoning) from the main answer.
        Returns (main_text, think_text) where think_text is None if no <think> tags found.
        """
                
        if not text:
            return "", None
        
        # Find all content inside <think>...</think>
        think_matches = self.THINK_PATTERN.findall(text)
        
        think_text = (
            "\n\n".join(m.strip() for m in think_matches)
            if think_matches
            else None
        )
        
        # Remove all <think> blocks from the original text
        main_text = self.THINK_PATTERN.sub("", text).strip()
        
        return main_text, think_text
    