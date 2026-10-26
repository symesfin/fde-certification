# Session 2: 🗃️ Dense Vector Retrieval

🎯 **Goal**: Understand RAG from first principles, in concepts and in code

📚 **Learning Outcomes**
- Introduction to Context Engineering, RAG, and the LLM application stack
- Overview of embeddings and similarity search
- Learn to add context using a vector database
- Build a RAG (dense vector retrieval) application from scratch in Python

🧰 **New Tools**
- Embedding Model: [OpenAI embeddings ](https://platform.openai.com/docs/guides/embeddings/what-are-embeddings#:~:text=*%2D-,ada,-%2D*%2D001)
- Orchestration: [OpenAI Python SDK](https://github.com/openai/openai-python)
- Vector Database: Custom

## 📛 Required Tooling & Account Setup
The same setup we saw in Session 1 is required here. You will need your dev environment ready to go and your OpenAI key. Everything else is Python!

## 📜 Recommended Reading

1. We _again_ recommend checking out the [Language Models are Few-Shot Learners (2020)](https://arxiv.org/abs/2005.14165) paper. As we'll discuss below, it literally invented In-Context Learning.
2. The [LLM Application Stack](https://a16z.com/emerging-architectures-for-llm-applications/) (based on the design pattern of In-Context Learning) by a16z (June 2023).
3. The OG RAG Paper is called [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (2020)](https://arxiv.org/abs/2005.11401). It's kind of the week of class for this one.
4. The original Context Engineering resource, [12-Factor Agents](https://github.com/humanlayer/12-factor-agents/tree/main) by Dex Horthy (June 2025).

# 🗺️ Overview

In Session 2, we dig deeper into prototyping LLM applications with Retrieval Augmented Generation, or RAG. From Session 1, we understand that we can write simple prompts and provide them to an LLM API. We can evaluate the output responses on behalf of our users with vibe checks. From The AIE Challenge, we know that we can wrap the functionality we iterate towards through prompting and vibe checking with a frontend and a deployed backend so that other people can use our app. Now, we'll see what happens when we  start adding the most appropriate context we can find. We should ask "what does the LLM need to know - that it doesn't already know - to give great outputs to users?" By augmenting our prompts with reference materials retrieved before generation, we do **RAG**.

The core **concepts** we’ll cover include the big ideas behind RAG. We break down RAG into two constituent components (processes): **in-context learning** and **embedding-based dense vector retrieval**.  

The **code** we’ll focus on during this session follows the concepts directly. We will develop a RAG application from scratch in pure Python. Starting first with a primer on understanding embeddings, we will proceed to build a custom **vector store**, implement a **similarity search engine**, and put it all together, Pythonically 🐍. You will be asked, as in Session 1, to enhance your Personal Wellness Assistant. As we will see, there are many ways to do this, even with a simple RAG application.

# 💬 From Prompt Engineering to RAG

> [!NOTE]
> Prompt Engineering = In-Context Learning

> [!NOTE]
> RAG = Dense Vector Retrieval + In-Context Learning

There is a lot we can do to improve the vibes by simply putting the right instructions in context. We can instruct the LLM about how we want outputs to feel to the user, and when the model should choose not to answer questions or engage with certain inputs. We can provide specific examples. All of this can be considered as adding context through prompt engineering. In other words, we add information directly to the context window, manually, in natural language.

Often, the information that we need to answer the question precisely for the user is not contained in our prompts. In that case, we're stuck relying on the model simply knowing the answer to the question. For this to be a possibility, the model must be trained on that specific information. In many environments that we'll work in as AI Engineers, much of the information we need to answer user queries is not publicly available, and therefore is not included in the model's training data.

**In these cases, the model must have access to information that it was not trained on.**

In other words, we must provide additional context to the model.

We can accomplish this in one of two ways: manually or automatically.

While Retrieval Augmented Generation, or RAG, technically relates to both of these situations, we should consider that _RAG is as a technique for automatically searching and retrieving information that we need to give the best response to the user._

## 🪟 **In-Context Learning**

**In-Context Learning** is a key concept that underlies all of Natural Language Processing. Indeed, it’s a key theme that underlies all building, shipping, and sharing of production LLM applications. The first key reference we need to be aware of is the GPT-3 paper entitled “Language Models are Few-Shot Learners” (2020) by Brown, et al. [[Ref](https://arxiv.org/abs/2005.14165)] The GPT-3 paper introduced the world to the idea of in-context learning for GPT-style transformers. It has continued to gain popularity over the years, as is evidenced from how many times you've heard the word `context` recently.

Interestingly, their definition of in-context learning is quite simple, and aligns directly with the one you’ll find on Wikipedia under Prompt Engineering.

> *In-context learning*, refers to a model's ability to temporarily learn from prompts. ~ Wikipedia, accessed March 2025 [[Ref](https://en.wikipedia.org/wiki/Prompt_engineering#In-context_learning)]
>

As is often true with foundational source materials, when we dig back into them there are additional details that shine in new contexts, and perhaps indicate something true about the tools we're using today to build production AI applications. For fun, and since I know that you won't actually read the GPT-3 paper, I'd like to encourage you to go with me on a brief journey from [Attention](https://arxiv.org/abs/1706.03762) to In-Context learning right now. Doing so will - and I'm being completely serious right now - give you amazing _context_ for everything that comes at you in Session 2. And it's a lot, so, buckle up.

As an introduction to this technical sidebar, we might consider that underneath in-context learning lies the attention mechanism. It is responsible for much of the magic behind the performance of LLMs today. When we input a sequence of text, we attend to each word relative to each other word. That is, we put a single word we’re attending to in its proper context, or simply “in context.”  Let us define context as the position of words within a sentence, the position of sentences within a paragraph, and so on. 

> _You shall know a word by the company it keeps._ ~ John Firth, A Synopsis of Linguistic Theory (1957)

This is an important concept when dealing with language in general and the meaning of words, and is especially important when trying to capture semantic meaning, as we do when creating embedding space representations. We need to create embedding representations of words to do retrieval for RAG.

<details>
<summary><strong> Technical Sidebar: Meta Learning, In-Context Learning, Train- and Test-Time Compute, and Reasoning</strong></summary>

<br/>

The ideas of meta-learning and in-context learning are very closely related and can be broadly understood by making a simple observation of humans. As people, we don’t need to be shown over and over, example after example, exactly how to do things. Although we need some supervision, we are all familiar with how it feels to have too much supervision and oversight, what we might call micro-managing. We don’t like this, and even as children, importantly, we don’t *need* this. Similarly, we don’t want to have to micromanage our LLMs.

> Humans do not require large supervised datasets to learn most language tasks – a brief directive in natural language … or at most a tiny number of demonstrations is often sufficient to enable a human to perform a new task to at least a reasonable degree of competence … this adaptability has practical advantages – it allows humans  
> to seamlessly mix together or switch between many tasks and skills, for example performing addition during a lengthy dialogue. To be broadly useful, we would someday like our NLP systems to have this same fluidity and generality. ~ GPT-3 Paper, 2020 [[Ref](https://arxiv.org/abs/2005.14165)]

In this, well, context, we can introduce the idea of meta-learning. Again, from the paper:

> One potential route towards addressing these issues is meta-learning – which in the context of language models means the model develops a broad set of skills and pattern recognition abilities at training time, and then uses those abilities at inference time to rapidly adapt to or recognize the desired task. ~ GPT-3 Paper, 2020 [[Ref](https://arxiv.org/abs/2005.14165)]

This distinction between acquiring skills and pattern recognition capabilities during training versus at inference is not only quite interesting academically, but it has real implications for building production LLM applications today.

It has become fashionable to refer to learning done during training as leveraging *train-time compute*, and learning done during inference similarly as *test-time* or *inference-time compute.* We can overlay these ideas directly on the inner- and outer-loops of meta learning, originally portrayed and described in Figure 1.1 of the GPT-3 paper, as shown below.

![Image](https://github.com/user-attachments/assets/5a77eee8-2629-4603-a72a-e6614b2c7588)

*Figure: Meta-learning as shown in the GPT-3 paper. Using terminology appropriate to today, we can think of the outer loop as leveraging train-time compute, and the inner loop as leveraging test-time compute.*

Train-time compute (outer loop meta-learning) has been scaled to such an enormous degree that most of the compute costs from training LLMs come from this gradient-based learning. The industry today is much more focused on leveraging test-time compute (inner-loop meta-learning) to dynamically infer on the fly. Concretely, *reasoning* capabilities that have appeared in leading LLMs - sometimes dubbed _thinking models_ - are capable of this inner-loop meta learning.

There are real cost implications to this distinction as well, because unsupervised pre-training updates made via outer-loop learning *require* enormous compute costs due to the backpropagation of gradient information through the LLM’s weights at each training step. In contrast, test-time compute during inference requires only forward passes through the model, and is able to effectively recognize patterns learned during training efficiently without paying gradient-update compute costs.

An investigation of the footnote of the GPT-3 paper tells us that meta-learning had previously been called zero-shot task transfer, a concept highly leveraged in the GPT-2 paper entitled “Language Models are Unsupervised Multitask Learners” (2019) by Radford, et al. [[Ref](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)]. The idea of something being “zero-shot” means that we only provide an instruction as input to the LLM, without any examples or demonstrations whatsoever. In other words, zero explicit supervision, zero micromanagement. We let the LLM do the work, as we do with simple instruction prompts, whether we’re using the outer-loop learning of an instruction-tuned model, or the inner-loop learning of a reasoning model. We have also seen the emergence of hybrid models that allow for dynamic switching inner- and outer-loop meta learning.

This is where the terminology gets quite confusing. We can do zero-shot learning in context that *still leverages* the inner-loop of meta learning — that is, test-time compute — with reasoning models. Traditionally, to leverage the inner loop in classic GPT-style models, we would need to use explicit prompting techniques to put examples *in-context*.

This idea of **explicitly** putting information in-context, this is the key to understanding why we talk about the modern LLM application stack being built on the design pattern of in-context learning.

We might say, rightfully, that as more production LLM applications are built with reasoning capabilities, the modern LLM application stack will be built on the design pattern of meta-learning.

To sum up, we quote the footnote on meta learning from the GPT-3 paper in its entirety:

> In the context of language models it has sometimes been called “zero-shot transfer”, but this term is potentially ambiguous: the method is “zero-shot” in the sense that no gradient updates are performed, but it often involves providing inference-time demonstrations to the model, so is not truly learning from zero examples. To avoid this confusion, we use the term “meta-learning” to capture the inner-loop / outer-loop structure of the general method, and the term “in context-learning” to refer to the inner loop of meta-learning. We further specialize the description to “zero-shot”, “one-shot”, or “few-shot” depending on how many demonstrations are provided at inference time. These terms are intended to remain agnostic on the question of whether the model learns new tasks from scratch at inference time or simply recognizes patterns seen during training – this is an important issue which we discuss later in the paper, but “meta-learning” is intended to encompass both possibilities, and simply describes the inner-outer loop structure. ~ GPT-3 Paper, 2020 [[Ref](https://arxiv.org/abs/2005.14165)]

What did they discuss later in the paper, you ask? In Section 5 on limitations, we read:

> A limitation, or at least uncertainty, associated with few-shot learning in GPT-3 is ambiguity about whether few-shot learning actually learns new tasks “from scratch” at inference time, or if it simply recognizes and identifies tasks that it has learned during training. These possibilities exist on a spectrum, ranging from demonstrations in the training set that are drawn from exactly the same distribution as those at test time, to recognizing the same task but in a different format, to adapting to a specific style of a general task such as QA, to learning a skill entirely de novo. Where GPT-3 is on this spectrum may also vary from task to task … Ultimately, it is not even clear what humans learn from scratch vs from prior demonstrations. ~ GPT-3 Paper, 2020 [[Ref](https://arxiv.org/abs/2005.14165)]

</details>

In the end, building performant and useful LLM applications is, indeed, all about putting the right stuff in context. As we will see, when building RAG applications, the retrieved context drives performance. Prioritizing what we put in context, or into an LLM’s context window, is extremely important. *Maybe, it’s the most important thing*. Garbage in, garbage out is still a rule of thumb for practitioners to live by, even in the age of generative AI.

## 🔢 Embeddings

Embedding models attempt to solve a simple problem: `computers can’t read or understand our text`.

Therefore, we must convert our text into a “machine-readable” format.  In other words, **we turn text into numbers** with embeddings. Another way to say this is that we move our data from natural language space to embedding space.

High-performance embedding models can convert text into numbers while maintaining **semantic and syntactic meaning** between words. The big idea is that the input (words) and output (numbers) must **mean the same thing**.

In embedding space, we want words or phrases with related meanings to be close to one another.  [A classic example](https://jalammar.github.io/illustrated-word2vec/#:~:text=We%20can%20visualize%20this%20analogy%20as%20we%20did%20previously%3A) that demonstrates how *semantic meaning* similarity **(rather than just syntactic similarity) can be maintained across embedding representation is from Word2Vec: `king - man + woman ~= queen`.

> Somewhat surprisingly, it was found that similarity of word representations goes beyond simple syntactic regularities. Using a word offset technique where simple algebraic operations are performed on the word vectors, it was shown for example that *vector(”King”) - vector(”Man”) + vector(”Woman”)* results in a vector that is closest to the vector representation of the word *Queen*.  ~ [Efficient Estimation of Word Representations in Vector Space, 2013](https://arxiv.org/abs/1301.3781)
>

The dimension of an embedding model is important because if there are too few dimensions, it becomes difficult to represent the rich complexity of the world of words! 

<details>
<summary><strong> The Meaning of Sentences</strong></summary>

<br/>

In practice, we do not often leverage words directly. Instead, the transformer typically processes tokens, or sub-words. Most embedding models that we use for similarity or retrieval (e.g., RAG) today are focused on the sentence level. In Sentence-BERT (2019) by Reimers and Gurevych [[Ref](https://arxiv.org/abs/1908.10084?utm_source=chatgpt.com)], which underlies Hugging Face’s powerful Sentence Transformers library [[Ref](https://huggingface.co/sentence-transformers)], one fixed-size vector representing each sentence is aggregated based on the matrix of token-level embeddings that BERT-style models output. In other words, we assemble embedding representations of sentences based on their constituent parts (tokens) to put together the meaning of the whole sequence.

</details>

In [leading state-of-the-art embedding models](https://huggingface.co/spaces/mteb/leaderboard) we often see many thousands of embedding dimensions.  Leading models have proven successful across many “downstream tasks,” which in the end, is what production LLM application development is all about.

Of course, only three dimensions can be visualized: a fundamental truth of our physical reality.  So, whether we’re dealing with many thousands of dimensions or just a few hundred (as in the Word2Vec [dataset](https://code.google.com/archive/p/word2vec/)), we always apply a compression algorithm like Principal Component Analysis (PCA) or t-distributed Stochastic Neighbor Embedding (t-SNE) to visualize it. 

Want to learn how to build, ship, and share Word2Vec-style embeddings from scratch?  Now is a good time to play with Word2Vec visually [here](https://projector.tensorflow.org/), or you can build your own from scratch [here](https://youtu.be/jh32bPiOXFQ?si=i_3ZUJ66p2O2hpph).

<details>
<summary><strong> The Meaning of Embeddings</strong></summary>

When you hear the word “embeddings,” what comes to mind?  An embedding *layer* within a transformer?  An embedding *model*, like the LLMs used for Retrieval Augment Generation (RAG) applications?  How about just an embedding *representation*?

Well, all of the above are correct.  As so many other things will throughout our time together, **the word “embeddings” depends on the context**.

Here’s our definition: 

- Def **embeddings**:(*used colloquially*) could mean **either** an *embedding* **layer** **(*within a transformer*) or an *embedding* **model**  **(*typically a BERT-style LLM*) depending on the context

Correspondingly, it’s important to consider a few other definitions, while we’re at it:

- Def **embedding representation**: a numerical (vector) representation of natural language that *preserves key relationships between words*
- Def **embedding layer**: a **trainable layer** *in a transformer* that maps input tokens to dense vector embedding representations
- Def **Embedding Model**: a **language model** (typically BERT-style) that *generates embedding representations* so that input and output have similar semantic meaning and are close together in embedding space

Embeddings, in the end, are all about turning words into numbers.  Whether we have a layer *within* an LLM or an entire encoder-only, BERT-style LLM, we’re creating embedding representations that we can use for computations.

Embeddings encode meaning with numbers, and that’s why we like them.

<br/>
</details>

# 🗂️ Retrieval Augmented Generation (RAG)

An easy way to think about RAG is that it attempts to solve a simple problem:  LLMs lie. I mean, they [hallucinate](https://openai.com/index/why-language-models-hallucinate/). I mean [confabulate](https://en.wikipedia.org/wiki/Confabulation). 

We can define a **hallucinations** (e.g., a bald-faced lie) as false, confident responses from LLMs. ✅ Fact-checking is one way to avoid this problem, in life as in LLM app dev.

RAG is for fact-checking LLMs. We can search for the facts. In RAG, we ***Retrieve*** the relevant reference documents, then we ***Augment*** the prompt with those references.  This improves our ***Generations**.* The idea of searching for relevant facts we need is not new, and we've been doing [Information Retrieval](https://en.wikipedia.org/wiki/Information_retrieval) for a long time.

Alternatively, in technospeak:
> "[LLMs'] ability to access and precisely manipulate knowledge is still limited, and hence on knowledge-intensive tasks, their performance lags behind task-specific architectures,"[[The RAG Paper Abstract](https://arxiv.org/abs/2005.11401)]

_Aside: one "task-specific architecture" for information retrieval we will see later in this course is called [Best-Matching 25 (BM25)](https://en.wikipedia.org/wiki/Okapi_BM25). Guess what it does!_

So RAG is about giving the LLMs access to new knowledge. We break down Retrieval Augmented Generation into two pieces: embedding-based dense vector retrieval and in-context Learning.

> RAG = Dense Vector Retrieval + In-Context Learning

Hopefully, the context provided by this session sheet is starting to come together for you: Word2Vec is one of the most iconic and earliest examples of dense vectors representing text. In-Context Learning was pioneered in [the GPT-3 Paper](https://arxiv.org/abs/2005.14165), and is all about putting relevant information into the context window.

The process of RAG for Question Answering works as follows:

1. Create **Database**
    1. Chunk and embed your documents
2. Ask **Question**
    1. Chunk and embed your question text
3. Find **References**
    1. Compare the embedding representations from your question and your chunked data
    2. Identify related context (in embedding space) 
4. **Augment** the Prompt
    1. Convert context from embedding space back into to natural language text
    2. Add reference material to the prompt
5. **Generate** a better answer!

If we can improve retrieval, then we can get better generations.

As we can see, the pattern we learned in Session 1 works directly with the pattern we’ll learn in Session 2 👇.  This is a meta-pattern we will continue to see at work!

<p align="center">
  <img src="https://github.com/user-attachments/assets/c6edd69b-a7d1-48bc-8865-f80094ce5003" width="45%" />
  <img src="https://github.com/user-attachments/assets/e04c2f8e-11d8-4803-ad1a-02b2fdca989e" width="45%" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/08769d55-3d74-476b-8258-c1ab3b76efa6" width="80%" />
</p>

# 🏗️ The LLM Application Stack

The LLM App stack is built on the design pattern of in-context learning.

> 🧰 Tools are replaceable; core concepts and boilerplate code/pseudo-code are not.

The [LLM application stack](https://a16z.com/emerging-architectures-for-llm-applications/), outlined in a blog entitled “Emerging Architectures for LLM Applications” (2023) by Bornstein and Radovanovic, is a great way to communicate how to think about the architecture patterns used in typical production LLM applications. Orchestration is placed in the center, as in software development. We will return to this diagram for many different builds and tools; however, what is most important is to understand the *ideas* of playing with prompts, how to use embedding models, working with vector databases, LLM APIs, providers of open- and close-source models, serving applications and models to our users, and collecting logs, validating outputs, and implementing caches when we do.

--

Do you have any questions about how to best prepare for Session 2 after reading? Please don't hesitate to provide direct feedback to `greg@aimakerspace.io` or `Dr Greg` on Discord!
