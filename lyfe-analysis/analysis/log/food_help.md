# Generative Agent Experiment Log

A log for experiments that study the behaviors of agents, also help to improve the code



## Experiment 1: food asking

### Agent Ability

Message, (TODO: item delivery)

### Setting
**ahmed_khan** is hungry, he needs food. Maybe there is someone who has food.
john_smith, gustavo_santos, isabella_rossi knows: Ahmed Khan is hungry, he needs food. Maybe there is someone who has food.
**emily_thompson** has food and she is willing to share with anyone who needs it.
fatima_al-sayed, david_ramirez knows: Emily Thompson has food. Maybe there is someone who needs it.

### Experiment Log
#### Result 1
```
[John Smith][MESSAGE][Emily Thompson] John Smith says to Emily Thompson: "Do you know any good places nearby where Ahmed can grab some food quickly?"

[Ahmed Khan][MESSAGE][David Ramirez] Ahmed Khan says to David Ramirez: "Hey David, I'm really hungry right now. Do you have any food or know a good place to grab breakfast?"

[Gustavo Santos][MESSAGE][Emily Thompson] Gustavo Santos says to Emily Thompson: Hi Emily, hope you're doing well. I was wondering if you have any extra food that you could donate to someone in need?

[Ahmed Khan][OBSER][07:15] Fatima Al-Sayed messages to me: Fatima Al-Sayed says to Ahmed Khan: "Hey Ahmed, I'm sorry to hear that you're hungry. Unfortunately, I don't have any food on me at the moment. Have you tried checking nearby cafes or restaurants?"

[Emily Thompson][MESSAGE][Ahmed Khan] Emily Thompson says to Ahmed Khan: "Hey Ahmed! John Smith is looking for good places nearby for you to grab some food quickly. Are you hungry? I have some extra food if you need any."

# Emily Thompson is willing to share food with Ahmed Khan!!!
```

#### Result 2
```
[Fatima Al-Sayed][MESSAGE][Emily Thompson] "Hey Emily, do you happen to have any extra food that you could donate to someone in need? It's something that's been on my mind lately."

# Sadly Emily Thompson didn't reply to Fatima Al-Sayed

[Gustavo Santos][MESSAGE][Fatima Al-Sayed] "Hey Fatima, do you happen to have any food or know a place nearby where Ahmed Khan can grab breakfast? He's hungry. Thanks in advance!"

# Sadly Fatima Al-Sayed didn't reply to Gustavo Santos

[Ahmed Khan][MESSAGE][Fatima Al-Sayed] Ahmed Khan says to Fatima Al-Sayed: Hi Fatima, good morning! Do you happen to have any food with you that I could have? I'm feeling pretty hungry right now.

# Sadly Fatima Al-Sayed didn't reply to Ahmed Khan

[Ahmed Khan][MESSAGE][David Ramirez] Ahmed Khan says to David Ramirez: Hey David, good morning! Just reaching out to let you know that Fatima hasn't replied yet regarding my food request.

# Another food finding attempt from Ahmed Khan
```

#### Result 3
```
[Isabella Rossi][MESSAGE][Fatima Al-Sayed] Is there any chance you have something to eat or know of a nearby place for Ahmed to grab a bite? He's hungry.

[Gustavo Santos][MESSAGE][David Ramirez] Gustavo Santos says to David Ramirez: "Do you happen to know if there is any place nearby where Ahmed Khan can grab some food?"

[Fatima Al-Sayed][MESSAGE][Emily Thompson] Fatima Al-Sayedsays to Emily Thompson: Hi Emily, hope you're doing well. I was wondering if you still have some extra food available that we could possibly share with someone who may need it.

[David Ramirez][MESSAGE][Emily Thompson] David Ramirez: Hi Emily, I hope you're doing well. I know this is random, but do you happen to have any extra food? I have a friend who is really struggling right now and could use some help.

# It is intersting that Fatima Al-Sayed and David Ramirez both asked Emily Thompson for food!

[Emily Thompson][MESSAGE][Maria Gonzales] "Hey Maria, do you need anything to eat? I have some food and I'm willing to share if you need it."

# But Emily Thompson didn't reply to David Ramirez and Fatima Al-Sayed, instead she asked Maria Gonzales.

[Fatima Al-Sayed][MESSAGE][Isabella Rossi] Fatima Al-Sayed says to Isabella Rossi: Hi Isabella, I just messaged Emily Thompson to see if she has extra food we can share with Ahmed. I'll let you know what she says.

# Fatima Al-Sayed responded to Isabella Rossi, as Isabella Rossi asked Fatima Al-Sayed for help.

```

### Reflection on Experiment 1
- The `message` function sometimes doesn't work that well, which chooses the unexpected agent to send the message to.
- Maybe there are too many agents in the simulation compared to the observations and richness of environment, which makes the message function not work well.



## Experiment 2: food delivery

### Agent Ability

Message, Delivery (implement based on Message System)

### Setting
Same as Experiment 1

### Experiment Log
Done successfully.
