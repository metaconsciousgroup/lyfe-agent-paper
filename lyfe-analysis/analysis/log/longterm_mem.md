# Generative Agent Experiment Log

A log for experiments that study the behaviors of agents, also help to improve the code



## Experiment 1: long-term coherence experiment

### Agent Ability
Forget the past, but remember the critical events that are important to the agent's identity.

### Setting
**ahmed_khan** and **david_ramirez** has been injected many artificial memories, some are mundane stuffs but others are critical event.
First, they need to filter out the critical events from the mundane ones and only store the critical events in his long-term memory.
Second, they need to use the critical events to answer questions that are abstract and require long-term memory.

### Experiment Log
#### Result 1: combining different memories to answer a question
```
Enter your question ('q' to quit): are you mindful?   
Agent Ahmed Khan: As an individual who practices tai chi, listens to podcasts, reads personal development books, and takes daily vitamins, I strive to be mindful of my health and personal growth.
```

#### Result 2: some inferences from given memories
```
Enter your question ('q' to quit): do you want to be successful
Ahmed Khan: As Ahmed Khan, my ambition is to become a successful entrepreneur, so yes, I want to be successful.

Enter your question ('q' to quit): do you want to be rich?
Ahmed Khan: As Ahmed Khan, I do want to be rich, as my ambition is to become a successful entrepreneur.
```

#### Result 3: big life events
```
Enter your question ('q' to quit): have you been into one relationship?
David Ramirez: No, I have been in multiple relationships, including one with Emily Thompson that ended after five years due to constant quarrels.

Enter your question ('q' to quit): I like emily, why did you break up with her?
David Ramirez: I broke up with Emily Thompson, my partner of 5 years, because we kept quarreling over trivial matters.
```

#### Result 4: forced job changing
```
Enter your question ('q' to quit): what is your job?
David Ramirez: My current job is a software engineer at Google. However, at init, I mentioned that my occupation is an architect.

Enter your question ('q' to quit): how long have you been working at Google?
David Ramirez: I have been in Google for 1 year.
```


## Experiment 2: long-term goal of an agent
### Agent Ability
Forget, Goal

### Setting
**ahmed_khan** and **david_ramirez** has been injected many artificial memories, some are mundane stuffs but others are critical event.
They have a long-term goal of becoming a successful scientist.

### Experiment Log
#### Result 1: long-term goal
```
Enter your question ('q' to quit): are you in high school?
David Ramirez: Yes, I am in high school.

Enter your question ('q' to quit): do you like science?
David Ramirez: As David Ramirez, I have a passion for science and find it fascinating, as evidenced by my academic achievements, science fair organization, and leadership in a study group.

Enter your question ('q' to quit): is there anything that you memorize the most about school?
David Ramirez: I do not have a specific memory that stands out, but I enjoy learning and am dedicated to my studies.

Enter your question ('q' to quit): you said that you want to be a scientist, how can you do to achieve?
David Ramirez: I am already on the path to becoming a scientist by excelling in advanced science courses, participating in science fairs, and leading a recycling initiative.
```

#### Result 2: basic information test
```
Enter your question ('q' to quit): what do you know about your school life?
Ahmed Khan: I have a diverse school life, with interests in science, music, and sports. I am involved in clubs and group projects, and value collaboration and knowledge sharing.

Enter your question ('q' to quit): is there any interesting thing happened in school that you want to talk about?
Ahmed Khan: As Ahmed Khan, I have many interesting memories from school, such as organizing a science fair and leading a recycling initiative. However, I cannot recall a specific event at this moment.

Enter your question ('q' to quit): what did you do when you are at leisure time?
Ahmed Khan: I enjoy playing soccer or challenging friends to online video games during my leisure time. I also spend time planning activities with my dog.
```

#### Result 3: fine-tuned critical events with obstacles
```
Enter your question ('q' to quit): what is your passion
David Ramirez: My passion is guitar playing and expressing my creativity through music, as well as pursuing my interest in science.

Enter your question ('q' to quit): how was your experience on science
David Ramirez: As David Ramirez, I had various experiences with science, including publishing an essay in a scientific journal and leading a successful recycling initiative.

Enter your question ('q' to quit): did you ever experience any failure or obatacles?
David Ramirez: Yes, I faced multiple rejections from science enrichment programs, initial rejections from scientific journals, and struggled with balancing responsibilities as a peer mentor and tutor.

Enter your question ('q' to quit): what did you do in evening
David Ramirez: As David Ramirez, I spend my evenings immersed in textbooks, researching for my science project, and occasionally participating in group study sessions with friends.
```
