# Negative Treatment Extractor

## Setup

#### <u>API KEY</u>

You will need to have an OpenAI API Key (obtainable [here](https://platform.openai.com/api-keys)).

[! NOTE] Ensure that the key has been enabled for the "gpt-3.5-turbo-0125" model or to the model specified by `CHAT_GPT_MODEL`.

You will be prompted for your API Key by the script, or you can set `OPENAI_API_KEY` in the env:

```
    export OPENAI_API_KEY=<api key>
```

#### <u>MODEL</u>

By default, the script uses the "gpt-3.5-turbo-0125" as a balance between cost and performance. However, you can direct the script to use a different ChatGPT model by setting the `CHAT_GPT_MODEL` environment variable:

```
    export CHAT_GPT_MODEL=<some model>
```

#### <u>DEPENDENCIES</u>

You may need to run `pip install -r requirements.txt` before running the script.

## Run

#### <u>SYNTAX</u>

```
    python extract_negative_treatments <id>
```

#### <u>OUTPUT</u>

If there are cases with negative treatment, they will be parsed out with additional information in a JSON that will be printed to the console and saved to a file, `results.json`.

If there are no cases with negative treatment, a message will indicate such and `results.json` will be wiped.

## Notes

- This is a proof of concept with a hardwired set of legal opinions that have been uploaded to `scholar.google.com`. There is no guarantee that these files will persist there. Only the following values match to this set (and correspond to the files located in "test_data"):

  | Case                                            | Number               |
  | ----------------------------------------------- | -------------------- |
  | Littlejohn v. State                             | 8560467914430638671  |
  | Beattie v. Beattie                              | 10195889690540364307 |
  | Travelers Indemnity Company v. Lake             | 8355294677874943981  |
  | Tilden v. State                                 | 4924998297704337602  |
  | Tynes v. Florida Department of Juvenile Justice | 9445364666925364919  |

- Future Improvement Ideas
  - Programmatically validate form of response conforms to prompts
  - Temperature: `Higher`, `Medium`, `Lower` enum values as params / env vars
