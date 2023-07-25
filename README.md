# gptgzip
Using ChatGPT 3.5 Turbo with Compress Data Packages
![image](https://github.com/graylan0/gptgzip/assets/34530588/da3c4fe1-a59e-4ae0-b8f9-92115797f9c5)

This Python script uses the OpenAI API and the gzip module to compress a text string and send it to the GPT-3.5-turbo model for processing. The text is first compressed using gzip, then converted to a string format that can be sent to the model. The model is informed via a system message that the user input is a GZIP encoded datapackage. The model's response is then printed out. However, as GPT-3.5-turbo is trained on regular text and not binary data, the effectiveness of this approach is experimental and the output may not be meaningful.
