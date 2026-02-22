# Simple text summarizer and financial advisor rewrite tool

# Example text - easy to swap out
EXAMPLE_TEXT = """
Artificial intelligence is transforming the financial services industry in unprecedented ways. 
Machine learning algorithms can now analyze vast amounts of market data in real-time, identifying 
patterns that human analysts might miss. Robo-advisors are becoming increasingly popular, offering 
automated investment advice at a fraction of the cost of traditional financial advisors. 
Blockchain technology is revolutionizing how transactions are processed, making them faster and more secure. 
However, there are concerns about data privacy and the potential for algorithmic bias. 
Regulators are working to establish frameworks that balance innovation with consumer protection. 
Despite these challenges, the adoption of AI in finance continues to accelerate, with major banks 
investing billions in technology infrastructure. The future of finance will likely be a hybrid model, 
combining human expertise with AI-powered tools to deliver better outcomes for clients.
"""

def summarize_to_bullets(text, num_bullets=5):
    """Extract key points from text and format as bullet points."""
    # Simple approach: split into sentences and take key ones
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    # Take first, middle, and last sentences to get a good spread
    if len(sentences) <= num_bullets:
        selected = sentences
    else:
        # Distribute evenly across the text
        step = len(sentences) // num_bullets
        selected = [sentences[i * step] for i in range(num_bullets)]
    
    # Format as bullet points
    bullets = []
    for i, sentence in enumerate(selected[:num_bullets], 1):
        bullets.append(f"• {sentence}")
    
    return "\n".join(bullets)

def rewrite_for_financial_advisor(summary):
    """Rewrite summary in concise, business-focused language for financial advisors."""
    # Replace casual language with business terminology
    replacements = {
        "is transforming": "disrupting",
        "can now": "enables",
        "are becoming": "emerging as",
        "are working": "developing",
        "will likely": "expected to",
        "better outcomes": "superior ROI",
    }
    
    rewritten = summary
    for old, new in replacements.items():
        rewritten = rewritten.replace(old, new)
    
    # Add financial advisor context
    lines = rewritten.split('\n')
    advisor_lines = []
    for line in lines:
        if line.strip():
            # Make it more action-oriented and concise
            advisor_lines.append(line.replace("•", "→"))
    
    return "\n".join(advisor_lines)

def process_text(text):
    """Process text: summarize and rewrite for financial advisor."""
    print("=" * 60)
    print("ORIGINAL TEXT:")
    print("=" * 60)
    print(text)
    print("\n")

    print("=" * 60)
    print("5 BULLET POINT SUMMARY:")
    print("=" * 60)
    summary = summarize_to_bullets(text)
    print(summary)
    print("\n")

    print("=" * 60)
    print("REWRITTEN FOR BUSY FINANCIAL ADVISOR:")
    print("=" * 60)
    advisor_version = rewrite_for_financial_advisor(summary)
    print(advisor_version)
    print("\n")

# Main execution - prompts for text input
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEXT SUMMARIZER")
    print("=" * 60)
    print("\nEnter your text below (press Enter twice when done, or just Enter to use example):")
    print("-" * 60)
    
    user_input = input().strip()
    
    # If user just presses Enter, use example text
    if not user_input:
        print("\nUsing example text...\n")
        text_to_process = EXAMPLE_TEXT
    else:
        # Collect multi-line input until empty line
        lines = [user_input]
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
        text_to_process = "\n".join(lines)
        print()
    
    process_text(text_to_process)
    
    print("=" * 60)
    print("CODE EXPLANATION:")
    print("=" * 60)
    print("""
1. summarize_to_bullets(): Splits text into sentences and selects key points
   evenly distributed across the text, then formats them as bullet points.

2. rewrite_for_financial_advisor(): Takes the summary and replaces casual
   language with business/financial terminology, making it more concise and
   action-oriented for busy professionals.

3. The script uses simple string operations - no external libraries needed.
   It's designed to be straightforward and easy to modify.

4. process_text(): Main function that takes any text input. The script prompts
   for text when run - press Enter twice or leave empty to use the example text.
""")
