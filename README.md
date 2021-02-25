






# teleg_chat_bot

This repository provides a reference implementation of *node2vec* as described in the paper:<br>
> the first version of telegram bot<br>
> answers the general questions<br>
> the accuracy of the answers is approximately 65%<br>
> the bot can give the weather in Moscow at the moment using OWM<br>
> <Insert paper link>

this bot works by selecting from the prepared replicas and calling the generative model, if it does not hit either one or the other, then a stub is selected

the dialogues.txt dataset can be downloaded on git [https://github.com/Koziev/NLP_Datasets/tree/master/Conversations/Data]

example of an echobot taken as a basis [https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py]
