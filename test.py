import regex as re
from collections import Counter

PAT = re.compile(r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")

def get_word_counts(input_path: str, special_tokens: list[str]):
    
    #todo: parallelize maybe
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
        return Counter()
    
    word_counts = Counter()
    
    special_pattern = "|".join(re.escape(s) for s in special_tokens)
    
    text_chunks = re.split(f'({special_pattern})', text)
    
    for chunk in text_chunks:
        
        if not chunk:
            continue

        if chunk in special_tokens:
            
            word_bytes = chunk.encode('utf-8')
            word_counts[word_bytes] += 1
            
        else:
            
            for match in PAT.finditer(chunk):
                
                word_bytes = match.group(0).encode('utf-8')
                word_counts[word_bytes] += 1
                
    return word_counts

def calc_pair_stats(words_split):
    
    pairs_count = Counter()
    
    for word_tuple, count in words_split.items():
        
        # skip words with no pairs
        if len(word_tuple) < 2:
            continue
        
        else:
            for i in range(len(word_tuple) -1):
                
                pair = (word_tuple[i], word_tuple[i+1])
        
                pairs_count[pair] += count
        
    return pairs_count
                


def merge(words_split, top_pair):
    
    new_words_split = {}
    
    new_token = top_pair[0] + top_pair[1]
    
    
    for word_tuple, count in words_split.items():
        
        new_word_parts = []
        i = 0
        while i < len(word_tuple):
            
            if i < len(word_tuple) - 1 and (word_tuple[i], word_tuple[i+1]) == top_pair:
                
                new_word_parts.append(new_token)
                
                i += 2
            
            else:
                
                new_word_parts.append(word_tuple[i])
                i+= 1
                
        new_words_split[tuple(new_word_parts)] = count
    
    return new_words_split            
    
    

def train_bpe(input_path: str, vocab_size: int, special_tokens: list[str]):
    
    vocab = {i: bytes([i]) for i in range(256)}
    for i, token_str in enumerate(special_tokens):
        vocab[256 + i] = token_str.encode('utf-8')
    
    merges = []
    
    word_counts = get_word_counts(INPUT_FILE, SPECIAL_TOKENS)
    
    
    special_tokens_bytes = {token.encode('utf-8') for token in special_tokens}
    
    words_split = {}
    
    for word_bytes, count in word_counts.items():
        
        if word_bytes in special_tokens_bytes:
            
            word_tuple = (word_bytes,)
            
        else:
            
            word_tuple = tuple(bytes([byte_val]) for byte_val in word_bytes)
            
        words_split[word_tuple] = count
    
    
    num_merges = vocab_size - len(vocab)
    
    for i in range(num_merges):
        
        pairs_count = calc_pair_stats(words_split)
    
    
        if not pairs_count:
        
            break
    
        top_pair = max(pairs_count.keys(), key=lambda p: (pairs_count[p], p))

    
        words_split = merge(words_split, top_pair)
        
        merges.append(top_pair)
        
        new_token_id = len(vocab)
        new_token_bytes = top_pair[0] + top_pair[1]
        vocab[new_token_id] = new_token_bytes
        
        if (i + 1) % 50 == 0:
            print(f"Merge {i+1}/{num_merges}: Merged {top_pair}")
    

    return vocab, merges

if __name__ == '__main__':
    INPUT_FILE = "TinyStories-valid.txt"
    SPECIAL_TOKENS = ["<|endoftext|>"]
    VOCAB_SIZE = 1000
    
    vocab, merges = train_bpe(INPUT_FILE, VOCAB_SIZE, SPECIAL_TOKENS)
    
    
    
    
    
