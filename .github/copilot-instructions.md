# SetForge - Quality Dataset Generator for Mistral 7B Fine-tuning

## 🎯 **PROJECT MISSION**
Generate 15K-20K high-quality Q&A pairs for fine-tuning Mistral 7B to outperform GPT/Gemini/Claude on Indian university guidance for Bangladeshi students. Budget: $200 DigitalOcean API. Timeline: 2-3 weeks.

## 📚 **RESEARCH-BASED QUALITY APPROACH**

### **Quality Dataset Principles (Based on Research)**
Based on [Hamel's Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/index.html) and [Meta's PEFT fine-tuning research](https://ai.meta.com/blog/how-to-fine-tune-llms-peft-dataset-curation/):

1. **Error Analysis First:** Systematic examination of failures reveals highest-ROI improvements
2. **Quality Over Quantity:** Clean, relevant data outperforms large, noisy datasets
3. **Context Grounding:** All answers must be extractable from source material
4. **Cultural Authenticity:** Domain-specific relevance for target audience
5. **Consistent Formatting:** Proper Mistral 7B instruction format is critical

### **Mistral 7B Instruction Format (CRITICAL)**
Based on [Mistral fine-tuning documentation](https://github.com/mistralai/mistral-finetune) and [HuggingFace discussions](https://discuss.huggingface.co/t/mistralai-mistral-7b-instruct-v0-2-fine-tuning-prompt-format/68899):

```json
{
  "instruction": "<s>[INST] What are the admission requirements for B.Tech at Sharda University? [/INST]",
  "input": "[Context from educational file about Sharda University admission]",
  "output": "Based on the information provided, the admission requirements for B.Tech at Sharda University include...",
  "context_source": "sharda_admission_process.txt",
  "university": "Sharda University",
  "question_type": "admission",
  "persona": "high_achiever"
}
```

## 🏗️ **ARCHITECTURE - QUALITY-FIRST DESIGN**

### **Core Components (Minimal, Focused)**
```python
main_generator.py     # Single, clean Q&A generator with quality focus
quality_checker.py    # Error analysis and quality validation
cli.py               # Simple commands: generate, validate, analyze
config.yaml          # Single configuration with quality thresholds
utils.py             # Cultural context and text processing utilities
```

### **Quality Pipeline Architecture**
```
48 Educational Files → Context Chunking → Quality Q&A Generation → Error Analysis → JSONL Dataset
```

## 🔧 **DIGITALOCEAN API INTEGRATION (CORRECT ENDPOINTS)**

### **API Configuration (EXACT ENDPOINTS)**
Based on [DigitalOcean serverless inference documentation](https://docs.digitalocean.com/products/gradientai-platform/how-to/use-serverless-inference/#create):

```yaml
# CORRECT API Configuration
api_url: "https://inference.do-ai.run/v1/chat/completions"  # ✅ CORRECT
model: "llama3-8b-instruct"  # ✅ CORRECT MODEL
max_cost_usd: 200.0  # Hard budget limit
cost_per_token: 0.0000002  # $0.20 per million tokens
```

### **API Call Pattern (Quality-Focused)**
```python
# Pattern: Quality-focused API calls with error analysis
async def generate_quality_qa(self, context_chunk: str) -> QAPair:
    # Generate question from context
    question = await self.generate_question(context_chunk)
    
    # Generate answer from same context (anti-hallucination)
    answer = await self.generate_answer(context_chunk, question)
    
    # Validate quality before saving
    quality_score = self.validate_qa_quality(question, answer, context_chunk)
    
    if quality_score >= self.config.min_quality_threshold:
        return QAPair(question, answer, context_chunk, quality_score)
    else:
        # Log for error analysis
        self.log_quality_failure(question, answer, quality_score)
        return None
```

## 🎯 **QUALITY GENERATION WORKFLOW**

### **1. Context Processing (Quality-First)**
```python
# Pattern: Meaningful context chunking
def create_quality_chunks(self, text: str) -> List[str]:
    """Create 500-1000 word chunks that preserve context integrity"""
    chunks = []
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    for paragraph in paragraphs:
        if len(current_chunk + paragraph) > 1000:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
```

### **2. Q&A Generation (Anti-Hallucination)**
```python
# Pattern: Context-grounded Q&A generation
async def generate_question_from_context(self, context: str) -> str:
    prompt = f"""
    Based on this context about Indian universities for Bangladeshi students, 
    generate a realistic question that a Bangladeshi student would ask.
    
    Context: {context}
    
    Generate a specific, actionable question that can be answered from this context.
    Focus on: admission requirements, fees, scholarships, visa process, or campus life.
    """
    
    response = await self.call_digitalocean_api(prompt)
    return self.extract_question(response)

async def generate_answer_from_context(self, context: str, question: str) -> str:
    prompt = f"""
    Answer this question using ONLY information from the provided context.
    If the context doesn't contain enough information, say so clearly.
    
    Question: {question}
    Context: {context}
    
    Provide a detailed, accurate answer based on the context.
    Include specific details like fees, dates, requirements, etc.
    """
    
    response = await self.call_digitalocean_api(prompt)
    return self.extract_answer(response)
```

### **3. Quality Validation (Error Analysis)**
```python
# Pattern: Systematic quality validation
def validate_qa_quality(self, question: str, answer: str, context: str) -> QualityMetrics:
    """Comprehensive quality validation based on research"""
    
    # Extractive score (anti-hallucination)
    extractive_score = self.calculate_extractive_score(answer, context)
    
    # Cultural authenticity
    cultural_score = self.validate_bangladeshi_focus(question, answer)
    
    # Specific details
    detail_score = self.validate_specific_details(answer)
    
    # Overall quality
    overall_score = (extractive_score * 0.4 + cultural_score * 0.3 + detail_score * 0.3)
    
    return QualityMetrics(
        extractive_score=extractive_score,
        cultural_score=cultural_score,
        detail_score=detail_score,
        overall_score=overall_score
    )
```

## 🚨 **CRITICAL QUALITY REQUIREMENTS**

### **Quality Thresholds (Non-Negotiable)**
Based on [Cleanlab's LLM tuning data guide](https://cleanlab.ai/blog/filter-llm-tuning-data/):

```python
# Quality thresholds for production
MIN_EXTRACTIVE_SCORE = 0.6  # Anti-hallucination
MIN_CULTURAL_SCORE = 0.7    # Bangladeshi relevance
MIN_DETAIL_SCORE = 0.6      # Specific information
MIN_OVERALL_SCORE = 0.7     # Combined quality
```

### **Error Analysis Process (Systematic)**
Based on [Hamel's error analysis methodology](https://hamel.dev/blog/posts/field-guide/index.html):

```python
# Pattern: Systematic error analysis
def analyze_quality_failures(self, failed_pairs: List[QAPair]) -> ErrorAnalysis:
    """Analyze quality failures to identify improvement opportunities"""
    
    error_categories = {
        'low_extractive': [],
        'poor_cultural_focus': [],
        'missing_details': [],
        'hallucination': [],
        'irrelevant_content': []
    }
    
    for pair in failed_pairs:
        if pair.quality.extractive_score < 0.6:
            error_categories['low_extractive'].append(pair)
        elif pair.quality.cultural_score < 0.7:
            error_categories['poor_cultural_focus'].append(pair)
        # ... categorize other failures
    
    return ErrorAnalysis(error_categories)
```

## 🛠️ **DEVELOPER WORKFLOWS (QUALITY-FIRST)**

### **1. Development Testing (Error Analysis Focus)**
```bash
# Step 1: Generate small batch with error analysis
python cli.py generate data/educational/ output/test_100.jsonl --target 100 --budget 5

# Step 2: Analyze quality failures
python cli.py analyze-errors output/test_100.jsonl --output error_analysis.json

# Step 3: Improve based on error analysis
python cli.py generate data/educational/ output/test_100_v2.jsonl --target 100 --budget 5

# Step 4: Validate improvement
python cli.py validate output/test_100_v2.jsonl --threshold 0.7
```

### **2. Quality Validation Workflow**
```bash
# Comprehensive quality analysis
python cli.py validate dataset.jsonl --detailed-report quality_report.json

# Error analysis for improvement
python cli.py analyze-errors dataset.jsonl --output error_analysis.json

# Cultural authenticity check
python cli.py validate-cultural dataset.jsonl --output cultural_report.json
```

### **3. Production Scaling (Quality-Maintained)**
```bash
# Production run with quality monitoring
python cli.py generate data/educational/ output/dataset_15k.jsonl \
    --target 15000 --budget 200 --quality-threshold 0.7

# Real-time quality monitoring
python cli.py monitor-quality output/dataset_15k.jsonl --live
```

## 📊 **QUALITY METRICS & SUCCESS CRITERIA**

### **Quantitative Targets (Research-Based)**
- **Volume**: 15,000-20,000 high-quality Q&A pairs
- **Quality Score**: ≥0.7 overall quality average
- **Extractive Content**: ≥60% to prevent hallucinations
- **Cultural Relevance**: ≥70% Bangladeshi-focused content
- **Specific Details**: ≥60% contain concrete information
- **Cost Efficiency**: ≤$0.013 per Q&A pair

### **Domain-Specific Quality Requirements**
```python
# Indian university guidance must include:
✅ Specific university names (Sharda, Amity, Galgotias)
✅ Bangladeshi education context (SSC, HSC, Honors)
✅ Cost information (₹ amounts, scholarship details)
✅ Visa/immigration guidance (Bangladesh embassy process)
✅ Cultural considerations (halal food, prayer facilities)
✅ Practical utility (actionable, real-world guidance)
```

## ⚠️ **CRITICAL PITFALLS (AVOID THESE)**

### **1. API Endpoint (MUST BE EXACT)**
```yaml
❌ WRONG: "https://api.digitalocean.com/v2/inference"
✅ CORRECT: "https://inference.do-ai.run/v1/chat/completions"
```

### **2. Quality Shortcuts (NON-NEGOTIABLE)**
```python
❌ DANGEROUS: Skipping extractive validation
✅ MANDATORY: All answers must be grounded in context

❌ RISKY: Ignoring cultural authenticity
✅ REQUIRED: Bangladeshi student context validation

❌ POOR: Generic international student advice
✅ ESSENTIAL: Indian university system specifics
```

### **3. Error Analysis Neglect (CRITICAL)**
```python
❌ FAILURE: Generating without error analysis
✅ SUCCESS: Systematic error analysis and improvement

❌ WASTE: Ignoring quality failures
✅ VALUE: Learning from failures to improve quality
```

## 🔍 **MONITORING & DEBUGGING (QUALITY-FOCUSED)**

### **Quality Monitoring Dashboard**
```python
logger.info(f"""
Quality Generation Status:
- Q&A Pairs: {len(self.generated_pairs):,}/{self.config.target_pairs:,}
- Quality Score: {avg_quality:.2f}/1.0 (Target: ≥0.7)
- Extractive Score: {avg_extractive:.2f}/1.0 (Target: ≥0.6)
- Cultural Score: {avg_cultural:.2f}/1.0 (Target: ≥0.7)
- Cost: ${self.total_cost:.2f}/${self.config.max_cost_usd}
- Error Rate: {error_rate:.1f}% (Target: <5%)
""")
```

### **Error Analysis Commands**
```bash
# Detailed error analysis
python cli.py analyze-errors dataset.jsonl --detailed --output error_report.json

# Quality improvement recommendations
python cli.py quality-recommendations dataset.jsonl --output recommendations.json

# Cultural authenticity analysis
python cli.py cultural-analysis dataset.jsonl --output cultural_report.json
```

## 📚 **REFERENCE DOCUMENTATION**

### **Quality Dataset Research**
- [Hamel's Field Guide to Rapidly Improving AI Products](https://hamel.dev/blog/posts/field-guide/index.html)
- [Meta's PEFT Fine-tuning Research](https://ai.meta.com/blog/how-to-fine-tune-llms-peft-dataset-curation/)
- [Cleanlab's LLM Tuning Data Guide](https://cleanlab.ai/blog/filter-llm-tuning-data/)

### **Mistral 7B Fine-tuning**
- [Mistral Fine-tuning Documentation](https://github.com/mistralai/mistral-finetune)
- [HuggingFace Mistral Discussion](https://discuss.huggingface.co/t/mistralai-mistral-7b-instruct-v0-2-fine-tuning-prompt-format/68899)
- [Stanford Alpaca Research](https://github.com/tatsu-lab/stanford_alpaca)

### **DigitalOcean API Documentation**
- [Serverless Inference Guide](https://docs.digitalocean.com/products/gradientai-platform/how-to/use-serverless-inference/#create)
- [Pricing Information](https://docs.digitalocean.com/products/gradientai-platform/details/pricing/#serverless-inference)
- [Fine-tuning Tutorial](https://www.digitalocean.com/community/tutorials/fine-tune-llama-3)

### **Quality Evaluation**
- [OpenAI Model Optimization](https://platform.openai.com/docs/guides/model-optimization)
- [HuggingFace Trainer Documentation](https://huggingface.co/docs/transformers/main_classes/trainer)
- [Unsloth Dataset Guide](https://docs.unsloth.ai/basics/datasets-guide)

## 🎯 **SUCCESS DEFINITION**

**A production-ready, high-quality dataset enabling Mistral 7B to outperform GPT-4 specifically on Indian university guidance for Bangladeshi students, with superior cultural understanding, practical utility, and extractive accuracy.**

**Key Success Indicators:**
- ≥0.7 overall quality score
- ≥60% extractive content (anti-hallucination)
- ≥70% cultural authenticity (Bangladeshi focus)
- ≤$0.013 cost per Q&A pair
- 15K-20K high-quality pairs within $200 budget
- Ready for Mistral 7B fine-tuning with proper instruction format
