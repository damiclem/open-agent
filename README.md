# Open Agent

This is an example on how on how to set up a coding agent using only free, open source tools.

Although it proved to be useful for the author, it is not meant to be a solution for every use case.

It is not meant to be better than your favourite, commercial agent. 

Instead, it provides a solution which is independent from commercial actors and licenses. 

As licenses for commercial software are often slow to be retrieved, this should allow experimenting freely without a particularly high cost.

Finally, using local agents provides useful details on how coding agents work under the hood.

## Disclaimer

Before starting experimenting with any of the tools presented in this document, it is your responsibility to do you own risk and security assessment. The author takes no responsibility for that.

As it is generally good practice to know what is happening under the hood. The author suggest to take a look at IBM's series on AI. Most importantly, [the following video.](https://youtu.be/gUNXZMcd2jU?si=W7X_wshcBfTfETTD)

## Tools

The solution provided is composed of multiple different layers of tools, organised as follows:

1. **VSCode** a highly customisable, free and open-source IDE.

2. **continue.dev** a VSCode extension that allows to interact with AI coding agents and provides tools to them.

3. **llama-swap** allows to execute multiple models on the same machine, in parallel and on demand.

4. **llama.cpp** provides access to LLMs through HTTP APIs.

5. **LLM models** to provide answers to user prompts implement agentic behavior.

### VSCode 

VSCode is a popular open-source IDE with a lot of customisation options. It features a marketpalce for extensions and plugins, making it easy to install them.

**License: MIT** available at [https://github.com/microsoft/vscode/blob/main/LICENSE.txt](https://github.com/microsoft/vscode/blob/main/LICENSE.txt)

### continue.dev

continue.dev is a VSCode extension that allows to interact with AI coding agents. It provides access to read and write tools to the models. It features different modalities to regulate tool usage.

The extension needs to be informed on which model to query for every specific role. This happens by defining a `.yaml` configuration file.

**License: Apache 2.0** available at [https://github.com/continue-dev/continue.dev/blob/main/LICENSE](https://github.com/continue-dev/continue.dev/blob/main/LICENSE)

### llama-swap

**License: MIT** available at [https://github.com/mostlygeek/llama-swap/blob/main/LICENSE.md](https://github.com/mostlygeek/llama-swap/blob/main/LICENSE.md)

### llama.cpp

**License: MIT** available at [https://github.com/ggml-org/llama.cpp/blob/master/LICENSE](https://github.com/ggml-org/llama.cpp/blob/master/LICENSE)

### Models

Multiple models are used for different scopes. Details are as follows:

#### Qwen3.5 9B

This is the latest model in the Qwen family, developed by Alibaba Cloud. It is an open-weight model freaturing 9 bilion parameters.

It has been trained for **reasoning, vision and tool usage**. Thus, it makes it the ideal candidate for implementing coding agents among the 

**License: Apache 2.0** available at [https://huggingface.co/Qwen/Qwen3.5-397B-A17B/blob/main/LICENSE](https://huggingface.co/Qwen/Qwen3.5-397B-A17B/blob/main/LICENSE)

2. **Qwen2.5 Coder 3B Instruct**

This is an older release of the Qwen model. Having 1/3 of the parameters of the Qwen3.5 model it makes inference faster. Hence, it has been chosen to be used for autocompletion, while it is not involved in more complex tasks.

**License: non-commercial** available at [https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct-GGUF/blob/main/LICENSE](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct-GGUF/blob/main/LICENSE)

3. **Nomic Embed Text V1.5**

This models provides embeddings. This means, it converts pieces of text into vectors, that can then be compared among each other.

It is a rather small model, highly specified for and confined to this purpose.

**License: Apache 2.0** not available to download.

## Prerequisites

The whole stack is being used proficiently with the following hardware specifications.

```md
Chip: Apple M3
Memory: 16GB
```

The experience may vary on different hardware. With fewer resources, largest models might not be fully offloaded to GPU for inference purposes. This might make inference itself slower.

## Get started

The following steps will guide you on how to set a proper AI assistant in VSCode. All these steps have alternatives. The ones proposed here shocase the solution which better suits the author's requirements, to the best of his knowledge at the time the document has been written. 

1. Install _VSCode_ in case you don't have it installed already. [See further instructions.](https://code.visualstudio.com/docs/setup/setup-overview)

2. Install _continue.dev_ from the extensions marketplace in VSCode. [See further instructions.](https://marketplace.visualstudio.com/items?itemName=Continue.continue)

3. Install _llama.cpp_. [See further instructions.](https://github.com/ggml-org/llama.cpp/tree/master?tab=readme-ov-file#quick-start)

    _llama.cpp_ can start a single server to provide access to a given LLM on its own. 
    
    Since we would need multiple servers running on demand, then we will use _llama-swap_ to execute multiple `_llama.cpp_` servers.

4. Download the LLM models. Here, we will use _llama.cpp_ to download models from huggingface to the local machine.

    _llama-swap_ does not allow to download models from hugging face on demand. Hence, this step must be done manually for each model.

    However, this is useful to assess whether the model is working or not. Some downloaded model are not suitable for _llama.cpp_ as they do not fulfill the LLaMa specifications.

    In order to download a the three models described in `Tools > Models`, execute the following commands:

    ```bash
    # Download embedding model
    llama-cli -hf nomic-ai/nomic-embed-text-v1.5-GGUF:Q4_K_M
    # Download autocomplete model
    llama-cli -hf unsloth/Qwen2.5-Coder-3B-Instruct-GGUF:Q4_K_M
    # Download agent model
    llama-cli -hf unsloth/Qwen3.5-9B-GGUF
    ```

    The `-hf` argument allows to specify a model on HuggingFace. The `:Q4_K_M` postfix define quantisation. This has a direct impact on the size of the model. Please, refer to the rightmost part of the huggingface page of a specific model to check hardware compatibility.

    Using `llama.cpp` installed through **homebrew**, the download folder is set to `~/Library/Caches/llama.cpp`. This could vary. Another alternative would be to manually download the models to a user-defined folder.

5. Install _llama-swap_. [See further instructions.](https://github.com/mostlygeek/llama-swap?tab=readme-ov-file#homebrew-install-macoslinux)

6. Configure _llama_swap_ to serve the models downloaded in step 4. The configuration file in `llama-swap.yaml` allows to load all the three models on demand.

    Execute _llama-swap_ with the following command:
    ```bash
    llama-swap --config ./llama-swap.yaml --listen localhost:8080
    ```

    See further configuration options [here.](https://github.com/mostlygeek/llama-swap/blob/main/docs/configuration.md)

7. Configure _continue.dev_ extension for VScode to use various models provided by the _llama-swap_ server, for different roles.

A sample configuration is provided in `./continue/config.yaml`. To use this as global, default configuration, copy it in `/Users/$USER/.config/continue/config.yaml`, assuming a unix system is used.

It is also possible to instruct AI agent to always rely on rules defined per project. For example, clearly instructing an AI agent on always searching for a given file in `src/` would prevent him from scanning the whole root folder, making the whole searching process faster.

To do so, just create one or more markdown files in the `./continue/rules` folder detailing the desired ruleset. [See further information.](https://docs.continue.dev/guides/codebase-documentation-awareness).

## Known issues

### Context limitation

The `llama-swap.config` files defines the `--context` parameter to 48000 tokens. Good results have been obtained with smaller context of 12000 tokens as well.

In order to prevent filling up the context too quickly, it is to:

1. Instruct the model to be as concise as possible (Occam Razor).

2. Preferring targeted actions with limited scope, rather than broader, complex actions.

When an agent hits context limits, it throws an error. As generated tokens enter the context, then it there would be no place for newest ones. 

Rather than setting a larger context, it is possible to set the `--context-shift` argument in `llama-swap.config` configuration for Qwen3.5 model. 

As the model would then "forget" earlier tokens, it might tend allucinate. See further information [on model parameters.](https://github.com/ggml-org/llama.cpp/tree/master/tools/server)

### Tools mis-interpretation

`llama-swap` provides responses in _llama.cpp_ format. The `.continue/config.yaml` defines `provider: openai` instead. For this reason, each model must be referenced with `localhost:<port>`.

**Note** each model listed in `llama-swap.config` configuration takes a unique port number starting from `5800` (default) and incrementing by 1, according to its index.

This difference might lead to some tools to be mis-interpreted by continue. Few times, the extension failed to represent diffs in the chat when **streaming** is enabled (default).

Although this seem to have been mitigated by introducing the `--jinja` argument in the `llama-swap.config` configuration, setting an AI gateway on top of _llama-swap_ would probably be a better, more reliable solution.