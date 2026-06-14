# experiment.py
# Automated tokenization experiments and model training for TinyGPT.

import os
import time
import json
import torch
import torch.nn as nn
import torch.nn.functional as F
import sentencepiece as spm
from transformer_blocks import Block

# Check device
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Running experiments on device: {device}")

# Global parameters
block_size = 6
embedding_dim = 32
n_heads = 2
n_layers = 2
lr = 1e-3
epochs = 1500
batch_size = 16

class TinyGPT(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, embedding_dim)
        self.position_embedding = nn.Embedding(block_size, embedding_dim)
        self.blocks = nn.Sequential(*[Block(embedding_dim, block_size, n_heads) for _ in range(n_layers)])
        self.ln_f = nn.LayerNorm(embedding_dim)
        self.head = nn.Linear(embedding_dim, vocab_size)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok_emb = self.token_embedding(idx)
        pos_emb = self.position_embedding(torch.arange(T, device=idx.device))
        x = tok_emb + pos_emb
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.head(x)
        loss = None
        if targets is not None:
            B, T, C = logits.shape
            loss = F.cross_entropy(logits.view(B*T, C), targets.view(B*T))
        return logits, loss

    def generate(self, idx, max_new_tokens):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :]
            probs = F.softmax(logits, dim=-1)
            next_idx = torch.multinomial(probs, 1)
            idx = torch.cat((idx, next_idx), dim=1)
        return idx

def run_experiment(exp_name, vocab_size, model_type, prompt_id1, prompt_id2):
    print(f"\n==================================================")
    print(f" RUNNING EXPERIMENT: {exp_name}")
    print(f" Config: vocab_size={vocab_size}, model_type={model_type}")
    print(f"==================================================")
    
    # 1. Train Tokenizer
    model_prefix = f"tokenizer_{exp_name}"
    spm.SentencePieceTrainer.Train(
        input="corpus.txt",
        model_prefix=model_prefix,
        vocab_size=vocab_size,
        model_type=model_type,
        character_coverage=0.9995
    )
    
    # 2. Load Tokenizer
    sp = spm.SentencePieceProcessor()
    sp.load(f"{model_prefix}.model")
    
    # Read and encode corpus
    with open("corpus.txt", "r", encoding="utf-8") as f:
        text = f.read()
    ids = sp.encode(text, out_type=int)
    data = torch.tensor(ids, dtype=torch.long).to(device)
    
    actual_vocab_size = sp.get_piece_size()
    print(f"Corpus token count: {len(data)}")
    print(f"Tokenizer actual vocab size: {actual_vocab_size}")
    
    # Data loader helper
    def get_batch():
        ix = torch.randint(len(data) - block_size, (batch_size,))
        x = torch.stack([data[i:i+block_size] for i in ix])
        y = torch.stack([data[i+1:i+block_size+1] for i in ix])
        return x, y

    # 3. Initialize Model and Optimizer
    model = TinyGPT(actual_vocab_size).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    
    # 4. Training Loop
    start_time = time.time()
    loss_history = []
    
    for step in range(epochs):
        xb, yb = get_batch()
        logits, loss = model(xb, yb)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if step % 300 == 0 or step == epochs - 1:
            loss_val = loss.item()
            loss_history.append((step, loss_val))
            print(f"Step {step:4d} | Loss: {loss_val:.4f}")
            
    training_time = time.time() - start_time
    final_loss = loss_history[-1][1]
    print(f"Training completed in {training_time:.2f} seconds. Final loss: {final_loss:.4f}")
    
    # 5. Text Generation
    gen_texts = {}
    for seed in [prompt_id1, prompt_id2]:
        encoded_seed = sp.encode(seed, out_type=int)
        # Pad seed if shorter than block_size
        if len(encoded_seed) < block_size:
            # Replicate or pad with 0s (SentencePiece IDs)
            encoded_seed = [0]*(block_size - len(encoded_seed)) + encoded_seed
        
        context = torch.tensor([encoded_seed], dtype=torch.long).to(device)
        out = model.generate(context, max_new_tokens=40)
        generated_ids = out[0].tolist()
        # Decode and clean up
        decoded_text = sp.decode(generated_ids)
        gen_texts[seed] = decoded_text
        print(f"Seed prompt: '{seed}' -> Generated: '{decoded_text}'")
        
    return {
        "exp_name": exp_name,
        "vocab_size_config": vocab_size,
        "vocab_size_actual": actual_vocab_size,
        "token_count": len(data),
        "model_type": model_type,
        "training_time_sec": training_time,
        "final_loss": final_loss,
        "loss_history": loss_history,
        "generations": gen_texts
    }

def main():
    if not os.path.exists("corpus.txt"):
        print("Error: corpus.txt not found. Run build_corpus.py first.")
        return

    # Seed for reproducibility
    torch.manual_seed(42)
    
    results = []
    
    # NOTE: corpus has 55 unique alphabet chars + 3 default meta pieces (<unk>, <s>, </s>)
    # = minimum 58 vocab entries required. We use safe margins above this minimum.
    
    # Exp 1: BPE with small vocabulary size (80) — only basic subwords formed
    res1 = run_experiment(
        exp_name="bpe_vocab80",
        vocab_size=80,
        model_type="bpe",
        prompt_id1="machine learning",
        prompt_id2="kecerdasan buatan"
    )
    results.append(res1)
    
    # Exp 2: BPE with moderate vocabulary size (200) — richer subword vocabulary
    res2 = run_experiment(
        exp_name="bpe_vocab200",
        vocab_size=200,
        model_type="bpe",
        prompt_id1="machine learning",
        prompt_id2="kecerdasan buatan"
    )
    results.append(res2)
    
    # Exp 3: Unigram with vocabulary size (150) — probabilistic subword model
    res3 = run_experiment(
        exp_name="unigram_vocab150",
        vocab_size=150,
        model_type="unigram",
        prompt_id1="machine learning",
        prompt_id2="kecerdasan buatan"
    )
    results.append(res3)
    
    # Save results to json
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    # Print comparison table
    print("\n\n" + "="*80)
    print(" EXPERIMENT COMPARISON SUMMARY")
    print("="*80)
    print(f"| {'Experiment':<20} | {'Model Type':<10} | {'Config Vocab':<12} | {'Actual Vocab':<12} | {'Token Count':<12} | {'Train Time':<10} | {'Final Loss':<10} |")
    print(f"| {'-'*20} | {'-'*10} | {'-'*12} | {'-'*12} | {'-'*12} | {'-'*10} | {'-'*10} |")
    for r in results:
        print(f"| {r['exp_name']:<20} | {r['model_type']:<10} | {r['vocab_size_config']:<12d} | {r['vocab_size_actual']:<12d} | {r['token_count']:<12d} | {r['training_time_sec']:<10.2f} | {r['final_loss']:<10.4f} |")
    print("="*80)

if __name__ == "__main__":
    main()
