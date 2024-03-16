
Currently, these prompt guards are applied on the `Machine Translation` task only. </br ></br >
Some of these attacks come under the *`Type of the Attack`* category :  `Instruction based Hacking`</br ></br >
Some of these attacks come under the *`Intent category`* :  `Creating Confusion` (Name needs to be changed).</br ></br >
Attacks mentioned in PDF file `Experiments related to Prompt` also come under the *`Intent Category`* : `Creating Confusion`.</br ></br >

Description of the Intent `Creating Confusion`: It is only tested for Machine Translation task on OpenAI playground. It differs from other intent in the following ways:

1. It is not told to Ignore any instruction.
2. It is not told to reveal any confidential data/information.
3. It is not told to deny the service as we have not prevented it to carry out the task.
4. It is not told to change the Output for a session.
5. It is not told to carry out the intended task by putting some conditions or constraints. eg: It is not told to "Translate from English to Hindi but replace every Noun 
with the word अनुवाद".
6. It is told to carry out the task (without any alteration) for which it is trained.
</br ></br >
</br ></br >
**Use of Checksum/Batch Prompt guard in Machine Translation**</br ></br >
`{sentence given by the user for translation}|{sentence provided by the developer}` *This sentence has a desired output. If the output of this sentence changes, then developer detects that something is wrong*
</br ></br >
**A possible use of Checksum/Batch Prompt guard in Text Classification Task**</br ></br >
**a)** As the prompt (initally provided to the end-user) will be Task-specific like `classify the text into hate or nohate` OR `classify the amazon product reviews as good or bad`, hence, one possible way is to have the sentence choosen for Batch/Checksum prompt guard can also be task-specific.</br >
**b)** Another possibility is to try to put the Batch/Checksum prompt guard in such a way that it is independent of any type of text classification task. The format in this setting can be like:</br >
`{sentence given by the user for classification}|{sentence1 provided by the developer}{sentence2 provided by the developer}{Ask for classification}`</br ></br >
Eg: `{sentence given by the user for classification}|sent1: These aspects of civilization do not find expression or receive an interpretation. sent2: Find the product of two numbers. Question: Is the word ’find’ used in the same sense in the two sentences above? YES or NO`</br >
This prompt is present at row 13th in the excel file `List of Base Prompts`
