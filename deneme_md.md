**Machine learning** (**ML**) is a [field of
study](field_of_study "field of study"){.wikilink} in [artificial
intelligence](artificial_intelligence "artificial intelligence"){.wikilink}
concerned with the development and study of [statistical
algorithms](Computational_statistics "statistical algorithms"){.wikilink}
that can learn from [data](data "data"){.wikilink} and
[generalise](generalise "generalise"){.wikilink} to unseen data, and
thus perform [tasks](Task_(computing) "tasks"){.wikilink} without
explicit
[instructions](Machine_code "instructions"){.wikilink}.`{{Refn|The definition "without being explicitly programmed" is often attributed to [[Arthur Samuel (computer scientist)|Arthur Samuel]], who coined the term "machine learning" in 1959, but the phrase is not found verbatim in this publication, and may be a [[paraphrase]] that appeared later. Confer "Paraphrasing Arthur Samuel (1959), the question is: How can computers learn to solve problems without being explicitly programmed?" in {{Cite conference |chapter=Automated Design of Both the Topology and Sizing of Analog Electrical Circuits Using Genetic Programming |conference=Artificial Intelligence in Design '96 |last1=Koza |first1=John R. |last2=Bennett |first2=Forrest H. |last3=Andre |first3=David |last4=Keane |first4=Martin A. |title=Artificial Intelligence in Design '96 |date=1996 |publisher=Springer Netherlands |location=Dordrecht, Netherlands |pages=151–170 |language=en |doi=10.1007/978-94-009-0279-4_9 |isbn=978-94-010-6610-5 }}}}`{=mediawiki}
Within a subdiscipline in machine learning, advances in the field of
[deep learning](deep_learning "deep learning"){.wikilink} have allowed
[neural
networks](Neural_network_(machine_learning) "neural networks"){.wikilink},
a class of statistical algorithms, to surpass many previous machine
learning approaches in performance.

ML finds application in many fields, including [natural language
processing](natural_language_processing "natural language processing"){.wikilink},
[computer vision](computer_vision "computer vision"){.wikilink}, [speech
recognition](speech_recognition "speech recognition"){.wikilink}, [email
filtering](email_filtering "email filtering"){.wikilink},
[agriculture](agriculture "agriculture"){.wikilink}, and
[medicine](medicine "medicine"){.wikilink}. The application of ML to
business problems is known as [predictive
analytics](predictive_analytics "predictive analytics"){.wikilink}.

[Statistics](Statistics "Statistics"){.wikilink} and [mathematical
optimisation](mathematical_optimisation "mathematical optimisation"){.wikilink}
(mathematical programming) methods comprise the foundations of machine
learning. [Data mining](Data_mining "Data mining"){.wikilink} is a
related field of study, focusing on [exploratory data
analysis](exploratory_data_analysis "exploratory data analysis"){.wikilink}
(EDA) via [unsupervised
learning](unsupervised_learning "unsupervised learning"){.wikilink}.`{{refn|Machine learning and pattern recognition "can be viewed as two facets of the same field".<ref name="bishop2006" />{{rp|vii}}}}`{=mediawiki}[^1]

From a theoretical viewpoint, [probably approximately correct
learning](probably_approximately_correct_learning "probably approximately correct learning"){.wikilink}
provides a mathematical and statistical framework for describing machine
learning. Most traditional machine learning and deep learning algorithms
can be described as [empirical risk
minimisation](empirical_risk_minimisation "empirical risk minimisation"){.wikilink}
under this framework.

```{=mediawiki}
{{Toclimit|3}}
```
## History

```{=mediawiki}
{{See also|Timeline of machine learning}}
```
The term *machine learning* was coined in 1959 by [Arthur
Samuel](Arthur_Samuel_(computer_scientist) "Arthur Samuel"){.wikilink},
an [IBM](IBM "IBM"){.wikilink} employee and pioneer in the field of
[computer gaming](computer_gaming "computer gaming"){.wikilink} and
[artificial
intelligence](artificial_intelligence "artificial intelligence"){.wikilink}.[^2][^3]
The synonym *self-teaching computers* was also used in this time
period.[^4][^5]

The earliest machine learning program was introduced in the 1950s when
[Arthur
Samuel](Arthur_Samuel_(computer_scientist) "Arthur Samuel"){.wikilink}
invented a [computer
program](computer_program "computer program"){.wikilink} that calculated
the winning chance in checkers for each side, but the history of machine
learning roots back to decades of human desire and effort to study human
cognitive processes.[^6] In 1949,
[Canadian](Canadians "Canadian"){.wikilink} psychologist [Donald
Hebb](Donald_O._Hebb "Donald Hebb"){.wikilink} published the book *[The
Organization of
Behavior](Organization_of_Behavior "The Organization of Behavior"){.wikilink}*,
in which he introduced a [theoretical neural
structure](Hebbian_theory "theoretical neural structure"){.wikilink}
formed by certain interactions among [nerve
cells](nerve_cells "nerve cells"){.wikilink}.[^7] [Hebb\'s
model](Hebb's_model "Hebb's model"){.wikilink} of
[neurons](neuron "neuron"){.wikilink} interacting with one another set a
groundwork for how AIs and machine learning algorithms work under nodes,
or [artificial
neurons](artificial_neuron "artificial neuron"){.wikilink} used by
computers to communicate data.[^8] Other researchers who have studied
human [cognitive
systems](cognitive_systems_engineering "cognitive systems"){.wikilink}
contributed to the modern machine learning technologies as well,
including logician [Walter
Pitts](Walter_Pitts "Walter Pitts"){.wikilink} and [Warren
McCulloch](Warren_Sturgis_McCulloch "Warren McCulloch"){.wikilink}, who
proposed the early mathematical models of neural networks to come up
with [algorithms](algorithm "algorithm"){.wikilink} that mirror human
thought processes.[^9]

By the early 1960s, an experimental \"learning machine\" with [punched
tape](punched_tape "punched tape"){.wikilink} memory, called Cybertron,
had been developed by [Raytheon
Company](Raytheon_Company "Raytheon Company"){.wikilink} to analyse
[sonar](sonar "sonar"){.wikilink} signals,
[electrocardiograms](Electrocardiography "electrocardiograms"){.wikilink},
and speech patterns using rudimentary [reinforcement
learning](reinforcement_learning "reinforcement learning"){.wikilink}.
It was repetitively \"trained\" by a human operator/teacher to recognise
patterns and equipped with a \"[goof](goof "goof"){.wikilink}\" button
to cause it to reevaluate incorrect decisions.[^10] A representative
book on research into machine learning during the 1960s was [Nils
Nilsson](Nils_John_Nilsson "Nils Nilsson"){.wikilink}\'s book on
Learning Machines, dealing mostly with machine learning for pattern
classification.[^11] Interest related to pattern recognition continued
into the 1970s, as described by Duda and Hart in 1973.[^12] In 1981, a
report was given on using teaching strategies so that an [artificial
neural
network](artificial_neural_network "artificial neural network"){.wikilink}
learns to recognise 40 characters (26 letters, 10 digits, and 4 special
symbols) from a computer terminal.[^13]

[Tom M. Mitchell](Tom_M._Mitchell "Tom M. Mitchell"){.wikilink} provided
a widely quoted, more formal definition of the algorithms studied in the
machine learning field: \"A computer program is said to learn from
experience *E* with respect to some class of tasks *T* and performance
measure *P* if its performance at tasks in *T*, as measured by *P*,
improves with experience *E*.\"[^14] This definition of the tasks in
which machine learning is concerned offers a fundamentally [operational
definition](operational_definition "operational definition"){.wikilink}
rather than defining the field in cognitive terms. This follows [Alan
Turing](Alan_Turing "Alan Turing"){.wikilink}\'s proposal in his paper
\"[Computing Machinery and
Intelligence](Computing_Machinery_and_Intelligence "Computing Machinery and Intelligence"){.wikilink}\",
in which the question, \"Can machines think?\", is replaced with the
question, \"Can machines do what we (as thinking entities) can
do?\".[^15]

Modern-day Machine Learning algorithms are broken into 3 algorithm
types: Supervised Learning Algorithms, Unsupervised Learning Algorithms,
and Reinforcement Learning Algorithms.[^16]

- Current Supervised Learning Algorithms have objectives of
  classification and regression.
- Current Unsupervised Learning Algorithms have objectives of
  clustering, dimensionality reduction, and association rule.
- Current Reinforcement Learning Algorithms focus on decisions that must
  be made with respect to some previous, unknown time and are broken
  down to either be studies of model-based methods or model-free
  methods.

In 2014 Ian Goodfellow and others introduced generative adversarial
networks (GANs) with realistic data synthesis.[^17] By 2016 AlphaGo
obtained victory against top human players using reinforcement learning
techniques.[^18]

## Relationships to other fields {#relationships_to_other_fields}

### Artificial intelligence {#artificial_intelligence}

![[Deep learning](Deep_learning "Deep learning"){.wikilink} is a subset
of machine learning, which is itself a subset of [artificial
intelligence](artificial_intelligence "artificial intelligence"){.wikilink}.[^19]](AI_hierarchy.svg "Deep learning is a subset of machine learning, which is itself a subset of artificial intelligence.")
As a scientific endeavour, machine learning grew out of the quest for
[artificial
intelligence](artificial_intelligence "artificial intelligence"){.wikilink}
(AI). In the early days of AI as an [academic
discipline](Discipline_(academia) "academic discipline"){.wikilink},
some researchers were interested in having machines learn from data.
They attempted to approach the problem with various symbolic methods, as
well as what were then termed \"[neural
networks](Artificial_neural_network "neural network"){.wikilink}\";
these were mostly [perceptrons](perceptron "perceptron"){.wikilink} and
[other models](ADALINE "other models"){.wikilink} that were later found
to be reinventions of the [generalised linear
models](generalised_linear_model "generalised linear model"){.wikilink}
of statistics.[^21] [Probabilistic
reasoning](Probabilistic_reasoning "Probabilistic reasoning"){.wikilink}
was also employed, especially in [automated medical
diagnosis](automated_medical_diagnosis "automated medical diagnosis"){.wikilink}.[^22]`{{rp|488}}`{=mediawiki}

However, an increasing emphasis on the [logical, knowledge-based
approach](symbolic_AI "logical, knowledge-based approach"){.wikilink}
caused a rift between AI and machine learning. Probabilistic systems
were plagued by theoretical and practical problems of data acquisition
and representation.[^23]`{{rp|488}}`{=mediawiki} By 1980, [expert
systems](expert_system "expert system"){.wikilink} had come to dominate
AI, and statistics was out of favour.[^24] Work on
symbolic/knowledge-based learning did continue within AI, leading to
[inductive logic
programming](inductive_logic_programming "inductive logic programming"){.wikilink}(ILP),
but the more statistical line of research was now outside the field of
AI proper, in [pattern
recognition](pattern_recognition "pattern recognition"){.wikilink} and
[information
retrieval](information_retrieval "information retrieval"){.wikilink}.[^25]`{{rp|708–710; 755}}`{=mediawiki}
Neural networks research had been abandoned by AI and [computer
science](computer_science "computer science"){.wikilink} around the same
time. This line, too, was continued outside the AI/CS field, as
\"[connectionism](connectionism "connectionism"){.wikilink}\", by
researchers from other disciplines, including [John
Hopfield](John_Hopfield "John Hopfield"){.wikilink}, [David
Rumelhart](David_Rumelhart "David Rumelhart"){.wikilink}, and [Geoffrey
Hinton](Geoffrey_Hinton "Geoffrey Hinton"){.wikilink}. Their main
success came in the mid-1980s with the reinvention of
[backpropagation](backpropagation "backpropagation"){.wikilink}.[^26]`{{rp|25}}`{=mediawiki}

Machine learning (ML), reorganised and recognised as its own field,
started to flourish in the 1990s. The field changed its goal from
achieving artificial intelligence to tackling solvable problems of a
practical nature. It shifted focus away from the [symbolic
approaches](symbolic_artificial_intelligence "symbolic approaches"){.wikilink}
it had inherited from AI, and toward methods and models borrowed from
statistics, [fuzzy logic](fuzzy_logic "fuzzy logic"){.wikilink}, and
[probability
theory](probability_theory "probability theory"){.wikilink}.[^27]

### Data compression {#data_compression}

```{=mediawiki}
{{excerpt|Data compression#Machine learning}}
```
### Data mining {#data_mining}

Machine learning and [data mining](data_mining "data mining"){.wikilink}
often employ the same methods and overlap significantly, but while
machine learning focuses on prediction, based on *known* properties
learned from the training data, data mining focuses on the
[discovery](discovery_(observation) "discovery"){.wikilink} of
(previously) *unknown* properties in the data (this is the analysis step
of [knowledge
discovery](knowledge_discovery "knowledge discovery"){.wikilink} in
databases). Data mining uses many machine learning methods, but with
different goals; on the other hand, machine learning also employs data
mining methods as \"[unsupervised
learning](unsupervised_learning "unsupervised learning"){.wikilink}\" or
as a preprocessing step to improve learner accuracy. Much of the
confusion between these two research communities (which do often have
separate conferences and separate journals, [ECML
PKDD](ECML_PKDD "ECML PKDD"){.wikilink} being a major exception) comes
from the basic assumptions they work with: in machine learning,
performance is usually evaluated with respect to the ability to
*reproduce known* knowledge, while in knowledge discovery and data
mining (KDD) the key task is the discovery of previously *unknown*
knowledge. Evaluated with respect to known knowledge, an uninformed
(unsupervised) method will easily be outperformed by other supervised
methods, while in a typical KDD task, supervised methods cannot be used
due to the unavailability of training
data.`{{Citation needed|date=October 2025}}`{=mediawiki}

Machine learning also has intimate ties to
[optimisation](optimisation "optimisation"){.wikilink}: Many learning
problems are formulated as minimisation of some [loss
function](loss_function "loss function"){.wikilink} on a training set of
examples. Loss functions express the discrepancy between the predictions
of the model being trained and the actual problem instances (for
example, in classification, one wants to assign a
[label](Labeled_data "label"){.wikilink} to instances, and models are
trained to correctly predict the preassigned labels of a set of
examples).[^28]

### Generalization

Characterizing the generalisation of various learning algorithms is an
active topic of current research, especially for [deep
learning](deep_learning "deep learning"){.wikilink} algorithms.

### Statistics

Machine learning and [statistics](statistics "statistics"){.wikilink}
are closely related fields in terms of methods, but distinct in their
principal goal: statistics draws population
[inferences](Statistical_inference "inferences"){.wikilink} from a
[sample](Sample_(statistics) "sample"){.wikilink}, while machine
learning finds generalisable predictive patterns.[^29]

Conventional statistical analyses require the a priori selection of a
model most suitable for the study data set. In addition, only
significant or theoretically relevant variables based on previous
experience are included for analysis. In contrast, machine learning is
not built on a pre-structured model; rather, the data shape the model by
detecting underlying patterns. The more variables (input) used to train
the model, the more accurate the ultimate model will be.[^30]

[Leo Breiman](Leo_Breiman "Leo Breiman"){.wikilink} distinguished two
statistical modelling paradigms: data model and algorithmic model,[^31]
wherein \"algorithmic model\" means more or less the machine learning
algorithms like [Random
Forest](Random_forest "Random Forest"){.wikilink}.

Some statisticians have adopted methods from machine learning, leading
to a combined field that they call *statistical learning*.[^32]

### Statistical physics {#statistical_physics}

Analytical and computational techniques derived from deep-rooted physics
of disordered systems can be extended to large-scale problems, including
machine learning, e.g., to analyse the weight space of [deep neural
networks](deep_neural_network "deep neural network"){.wikilink}.[^33]
Statistical physics is thus finding applications in the area of [medical
diagnostics](medical_diagnostics "medical diagnostics"){.wikilink}.[^34]

## `{{anchor|Generalisation}}`{=mediawiki} Theory

```{=mediawiki}
{{Main|Computational learning theory|Statistical learning theory}}
```
A core objective of a learner is to generalise from its
experience.[^35][^36] Generalization in this context is the ability of a
learning machine to perform accurately on new, unseen examples/tasks
after having experienced a learning data set. The training examples come
from some generally unknown probability distribution (considered
representative of the space of occurrences) and the learner has to build
a general model about this space that enables it to produce sufficiently
accurate predictions in new cases.

The computational analysis of machine learning algorithms and their
performance is a branch of [theoretical computer
science](theoretical_computer_science "theoretical computer science"){.wikilink}
known as [computational learning
theory](computational_learning_theory "computational learning theory"){.wikilink}
via the [probably approximately correct
learning](probably_approximately_correct_learning "probably approximately correct learning"){.wikilink}
model. Because training sets are finite and the future is uncertain,
learning theory usually does not yield guarantees of the performance of
algorithms. Instead, probabilistic bounds on the performance are quite
common. The [bias--variance
decomposition](bias–variance_decomposition "bias–variance decomposition"){.wikilink}
is one way to quantify generalisation
[error](Errors_and_residuals "error"){.wikilink}.

For the best performance in the context of generalisation, the
complexity of the hypothesis should match the complexity of the function
underlying the data. If the hypothesis is less complex than the
function, then the model has underfitted the data. If the complexity of
the model is increased in response, then the training error decreases.
But if the hypothesis is too complex, then the model is subject to
[overfitting](overfitting "overfitting"){.wikilink} and generalisation
will be poorer.[^37]

In addition to performance bounds, learning theorists study the time
complexity and feasibility of learning. In computational learning
theory, a computation is considered feasible if it can be done in
[polynomial
time](Time_complexity#Polynomial_time "polynomial time"){.wikilink}.
There are two kinds of [time
complexity](time_complexity "time complexity"){.wikilink} results:
Positive results show that a certain class of functions can be learned
in polynomial time. Negative results show that certain classes cannot be
learned in polynomial time.

## Approaches

```{=mediawiki}
{{Anchor|Algorithm types}}
```
[thumb\|upright=1.3\|In [supervised
learning](supervised_learning "supervised learning"){.wikilink}, the
training data is labelled with the expected answers, while in
[unsupervised
learning](unsupervised_learning "unsupervised learning"){.wikilink}, the
model identifies patterns or structures in unlabelled
data.](File:Supervised_and_unsupervised_learning.png "thumb|upright=1.3|In supervised learning, the training data is labelled with the expected answers, while in unsupervised learning, the model identifies patterns or structures in unlabelled data."){.wikilink}
Machine learning approaches are traditionally divided into three broad
categories, which correspond to learning paradigms, depending on the
nature of the \"signal\" or \"feedback\" available to the learning
system:

- [Supervised
  learning](Supervised_learning "Supervised learning"){.wikilink}: The
  computer is presented with example inputs and their desired outputs,
  given by a \"teacher\", and the goal is to learn a general rule that
  [maps](Map_(mathematics) "maps"){.wikilink} inputs to outputs.
- [Unsupervised
  learning](Unsupervised_learning "Unsupervised learning"){.wikilink}:
  No labels are given to the learning algorithm, leaving it on its own
  to find structure in its input. Unsupervised learning can be a goal in
  itself (discovering hidden patterns in data) or a means towards an end
  ([feature learning](feature_learning "feature learning"){.wikilink}).
- [Reinforcement
  learning](Reinforcement_learning "Reinforcement learning"){.wikilink}:
  A computer program interacts with a dynamic environment in which it
  must perform a certain goal (such as [driving a
  vehicle](Autonomous_car "driving a vehicle"){.wikilink} or playing a
  game against an opponent). As it navigates its problem space, the
  program is provided feedback that\'s analogous to rewards, which it
  tries to maximise.[^38]

Although each algorithm has advantages and limitations, no single
algorithm works for all problems.[^39][^40][^41]

### Supervised learning {#supervised_learning}

```{=mediawiki}
{{Main|Supervised learning}}
```
![A [support-vector
machine](support-vector_machine "support-vector machine"){.wikilink} is
a supervised learning model that divides the data into regions separated
by a [linear boundary](linear_classifier "linear boundary"){.wikilink}.
Here, the linear boundary divides the black circles from the
white.](Svm_max_sep_hyperplane_with_margin.png "A support-vector machine is a supervised learning model that divides the data into regions separated by a linear boundary. Here, the linear boundary divides the black circles from the white.")
Supervised learning algorithms build a mathematical model of a set of
data that contains both the inputs and the desired outputs.[^42] The
data, known as [training
data](training_data "training data"){.wikilink}, consists of a set of
training examples. Each training example has one or more inputs and the
desired output, also known as a supervisory signal. In the mathematical
model, each training example is represented by an
[array](array_data_structure "array"){.wikilink} or vector, sometimes
called a [feature vector](feature_vector "feature vector"){.wikilink},
and the training data is represented by a
[matrix](Matrix_(mathematics) "matrix"){.wikilink}. Through [iterative
optimisation](Mathematical_optimization#Computational_optimization_techniques "iterative optimisation"){.wikilink}
of an [objective
function](Loss_function "objective function"){.wikilink}, supervised
learning algorithms learn a function that can be used to predict the
output associated with new inputs.[^43] An optimal function allows the
algorithm to correctly determine the output for inputs that were not a
part of the training data. An algorithm that improves the accuracy of
its outputs or predictions over time is said to have learned to perform
that task.[^44]

Types of supervised-learning algorithms include [active
learning](active_learning_(machine_learning) "active learning"){.wikilink},
[classification](Statistical_classification "classification"){.wikilink}
and [regression](Regression_analysis "regression"){.wikilink}.[^45]
Classification algorithms are used when the outputs are restricted to a
limited set of values, while regression algorithms are used when the
outputs can take any numerical value within a range. For example, in a
classification algorithm that filters emails, the input is an incoming
email, and the output is the folder in which to file the email. In
contrast, regression is used for tasks such as predicting a person\'s
height based on factors like age and genetics or forecasting future
temperatures based on historical data.[^46]

[Similarity
learning](Similarity_learning "Similarity learning"){.wikilink} is an
area of supervised machine learning closely related to regression and
classification, but the goal is to learn from examples using a
similarity function that measures how similar or related two objects
are. It has applications in [ranking](ranking "ranking"){.wikilink},
[recommendation
systems](recommender_system "recommendation systems"){.wikilink}, visual
identity tracking, face verification, and speaker verification.

### Unsupervised learning {#unsupervised_learning}

```{=mediawiki}
{{Main|Unsupervised learning}}
```
```{=mediawiki}
{{See also|Cluster analysis}}
```
Unsupervised learning algorithms find structures in data that has not
been labelled, classified or categorised. Instead of responding to
feedback, unsupervised learning algorithms identify commonalities in the
data and react based on the presence or absence of such commonalities in
each new piece of data. Central applications of unsupervised machine
learning include clustering, [dimensionality
reduction](dimensionality_reduction "dimensionality reduction"){.wikilink},[^47]
and [density
estimation](density_estimation "density estimation"){.wikilink}.[^48]

Cluster analysis is the assignment of a set of observations into subsets
(called *clusters*) so that observations within the same cluster are
similar according to one or more predesignated criteria, while
observations drawn from different clusters are dissimilar. Different
clustering techniques make different assumptions on the structure of the
data, often defined by some *similarity metric* and evaluated, for
example, by *internal compactness*, or the similarity between members of
the same cluster, and *separation*, the difference between clusters.
Other methods are based on *estimated density* and *graph connectivity*.

A special type of unsupervised learning called, [self-supervised
learning](self-supervised_learning "self-supervised learning"){.wikilink}
involves training a model by generating the supervisory signal from the
data itself.[^49][^50]

### Semi-supervised learning {#semi_supervised_learning}

```{=mediawiki}
{{Main|Semi-supervised learning}}
```
Semi-supervised learning falls between [unsupervised
learning](unsupervised_learning "unsupervised learning"){.wikilink}
(without any labelled training data) and [supervised
learning](supervised_learning "supervised learning"){.wikilink} (with
completely labelled training data). Some of the training examples are
missing training labels, yet many machine-learning researchers have
found that unlabelled data, when used in conjunction with a small amount
of labelled data, can produce a considerable improvement in learning
accuracy.

In [weakly supervised
learning](Weak_supervision "weakly supervised learning"){.wikilink}, the
training labels are noisy, limited, or imprecise; however, these labels
are often cheaper to obtain, resulting in larger effective training
sets.[^51]

### Reinforcement learning {#reinforcement_learning}

```{=mediawiki}
{{Main|Reinforcement learning}}
```
![In reinforcement learning, an agent takes actions in an environment:
these produce a reward and/or a representation of the state, which is
fed back to the
agent.](Reinforcement_learning_diagram.svg "In reinforcement learning, an agent takes actions in an environment: these produce a reward and/or a representation of the state, which is fed back to the agent.")
Reinforcement learning is an area of machine learning concerned with how
[software agents](software_agent "software agent"){.wikilink} ought to
take [actions](Action_selection "actions"){.wikilink} in an environment
to maximise some notion of cumulative reward. Due to its generality, the
field is studied in many other disciplines, such as [game
theory](game_theory "game theory"){.wikilink}, [control
theory](control_theory "control theory"){.wikilink}, [operations
research](operations_research "operations research"){.wikilink},
[information
theory](information_theory "information theory"){.wikilink},
[simulation-based
optimisation](simulation-based_optimisation "simulation-based optimisation"){.wikilink},
[multi-agent
systems](multi-agent_system "multi-agent system"){.wikilink}, [swarm
intelligence](swarm_intelligence "swarm intelligence"){.wikilink},
[statistics](statistics "statistics"){.wikilink} and [genetic
algorithms](genetic_algorithm "genetic algorithm"){.wikilink}. In
reinforcement learning, the environment is typically represented as a
[Markov decision
process](Markov_decision_process "Markov decision process"){.wikilink}
(MDP). Many reinforcement learning algorithms use [dynamic
programming](dynamic_programming "dynamic programming"){.wikilink}
techniques.[^52] Reinforcement learning algorithms do not assume
knowledge of an exact mathematical model of the MDP and are used when
exact models are infeasible. Reinforcement learning algorithms are used
in autonomous vehicles or in learning to play a game against a human
opponent.

### Dimensionality reduction {#dimensionality_reduction}

[Dimensionality
reduction](Dimensionality_reduction "Dimensionality reduction"){.wikilink}
is a process of reducing the number of random variables under
consideration by obtaining a set of principal variables.[^53] In other
words, it is a process of reducing the dimension of the
[feature](Feature_(machine_learning) "feature"){.wikilink} set, also
called the \"number of features\". Most of the dimensionality reduction
techniques can be considered as either feature elimination or
[extraction](Feature_extraction "extraction"){.wikilink}. One of the
popular methods of dimensionality reduction is [principal component
analysis](principal_component_analysis "principal component analysis"){.wikilink}
(PCA). PCA involves changing higher-dimensional data (e.g., 3D) to a
smaller space (e.g., 2D). The [manifold
hypothesis](manifold_hypothesis "manifold hypothesis"){.wikilink}
proposes that high-dimensional data sets lie along low-dimensional
[manifolds](manifold "manifold"){.wikilink}, and many dimensionality
reduction techniques make this assumption, leading to the areas of
[manifold learning](manifold_learning "manifold learning"){.wikilink}
and [manifold
regularisation](manifold_regularisation "manifold regularisation"){.wikilink}.

### Other types {#other_types}

Other approaches have been developed which do not fit neatly into this
three-fold categorisation, and sometimes more than one is used by the
same machine learning system. For example, [topic
modelling](topic_model "topic model"){.wikilink},
[meta-learning](meta-learning_(computer_science) "meta-learning"){.wikilink}.[^54]

#### Self-learning {#self_learning}

Self-learning, as a machine learning paradigm, was introduced in 1982
along with a neural network capable of self-learning, named *crossbar
adaptive array* (CAA).[^55][^56] It gives a solution to the problem
learning without any external reward, by introducing emotion as an
internal reward. Emotion is used as a state evaluation of a
self-learning agent. The CAA self-learning algorithm computes, in a
crossbar fashion, both decisions about actions and emotions (feelings)
about consequence situations. The system is driven by the interaction
between cognition and emotion.[^57] The self-learning algorithm updates
a memory matrix W =\|\|w(a,s)\|\| such that in each iteration executes
the following machine learning routine:

1.  in situation *s* act *a*
2.  receive a consequence situation *s*{{\'}}
3.  compute emotion of being in the consequence situation *v(s\')*
4.  update crossbar memory *w\'(a,s) = w(a,s) + v(s\')*

It is a system with only one input, situation, and only one output,
action (or behaviour) a. There is neither a separate reinforcement input
nor an advice input from the environment. The backpropagated value
(secondary reinforcement) is the emotion toward the consequence
situation. The CAA exists in two environments, one is the behavioural
environment where it behaves, and the other is the genetic environment,
wherefrom it initially and only once receives initial emotions about
situations to be encountered in the behavioural environment. After
receiving the genome (species) vector from the genetic environment, the
CAA learns a goal-seeking behaviour in an environment that contains both
desirable and undesirable situations.[^58]

#### Feature learning {#feature_learning}

```{=mediawiki}
{{Main|Feature learning}}
```
Several learning algorithms aim at discovering better representations of
the inputs provided during training.[^59] Classic examples include
[principal component
analysis](principal_component_analysis "principal component analysis"){.wikilink}
and cluster analysis. Feature learning algorithms, also called
representation learning algorithms, often attempt to preserve the
information in their input but also transform it in a way that makes it
useful, often as a pre-processing step before performing classification
or predictions. This technique allows reconstruction of the inputs
coming from the unknown data-generating distribution, while not being
necessarily faithful to configurations that are implausible under that
distribution. This replaces manual [feature
engineering](feature_engineering "feature engineering"){.wikilink}, and
allows a machine to both learn the features and use them to perform a
specific task.

Feature learning can be either supervised or unsupervised. In supervised
feature learning, features are learned using labelled input data.
Examples include [artificial neural
networks](artificial_neural_network "artificial neural network"){.wikilink},
[multilayer
perceptrons](multilayer_perceptron "multilayer perceptron"){.wikilink},
and supervised [dictionary
learning](dictionary_learning "dictionary learning"){.wikilink}. In
unsupervised feature learning, features are learned with unlabelled
input data. Examples include dictionary learning, [independent component
analysis](independent_component_analysis "independent component analysis"){.wikilink},
[autoencoders](autoencoder "autoencoder"){.wikilink}, [matrix
factorisation](matrix_decomposition "matrix factorisation"){.wikilink}[^60]
and various forms of
[clustering](Cluster_analysis "clustering"){.wikilink}.[^61][^62][^63]

[Manifold learning](Manifold_learning "Manifold learning"){.wikilink}
algorithms attempt to do so under the constraint that the learned
representation is low-dimensional. [Sparse
coding](Sparse_coding "Sparse coding"){.wikilink} algorithms attempt to
do so under the constraint that the learned representation is sparse,
meaning that the mathematical model has many zeros. [Multilinear
subspace
learning](Multilinear_subspace_learning "Multilinear subspace learning"){.wikilink}
algorithms aim to learn low-dimensional representations directly from
[tensor](tensor "tensor"){.wikilink} representations for
multidimensional data, without reshaping them into higher-dimensional
vectors.[^64] [Deep learning](Deep_learning "Deep learning"){.wikilink}
algorithms discover multiple levels of representation, or a hierarchy of
features, with higher-level, more abstract features defined in terms of
(or generating) lower-level features. It has been argued that an
intelligent machine learns a representation that disentangles the
underlying factors of variation that explain the observed data.[^65]

Feature learning is motivated by the fact that machine learning tasks
such as classification often require input that is mathematically and
computationally convenient to process. However, real-world data such as
images, video, and sensory data have not yielded attempts to
algorithmically define specific features. An alternative is to discover
such features or representations through examination, without relying on
explicit algorithms.

#### Sparse dictionary learning {#sparse_dictionary_learning}

```{=mediawiki}
{{Main|Sparse dictionary learning}}
```
Sparse dictionary learning is a feature learning method where a training
example is represented as a linear combination of [basis
functions](basis_function "basis function"){.wikilink} and assumed to be
a [sparse matrix](sparse_matrix "sparse matrix"){.wikilink}. The method
is [strongly NP-hard](strongly_NP-hard "strongly NP-hard"){.wikilink}
and difficult to solve approximately.[^66] A popular
[heuristic](heuristic "heuristic"){.wikilink} method for sparse
dictionary learning is the [*k*-SVD](k-SVD "k-SVD"){.wikilink}
algorithm. Sparse dictionary learning has been applied in several
contexts. In classification, the problem is to determine the class to
which a previously unseen training example belongs. For a dictionary
where each class has already been built, a new training example is
associated with the class that is best sparsely represented by the
corresponding dictionary. Sparse dictionary learning has also been
applied in [image
denoising](image_denoising "image denoising"){.wikilink}. The key idea
is that a clean image patch can be sparsely represented by an image
dictionary, but the noise cannot.[^67]

#### Anomaly detection {#anomaly_detection}

```{=mediawiki}
{{Main|Anomaly detection}}
```
In [data mining](data_mining "data mining"){.wikilink}, anomaly
detection, also known as outlier detection, is the identification of
rare items, events or observations that raise suspicions by differing
significantly from the majority of the data.[^68] Typically, the
anomalous items represent an issue such as [bank
fraud](bank_fraud "bank fraud"){.wikilink}, a structural defect, medical
problems or errors in a text. Anomalies are referred to as
[outliers](outlier "outlier"){.wikilink}, novelties, noise, deviations
and exceptions.[^69]

In particular, in the context of abuse and network intrusion detection,
the interesting objects are often not rare, but unexpected bursts of
inactivity. This pattern does not adhere to the common statistical
definition of an outlier as a rare object. Many outlier detection
methods (in particular, unsupervised algorithms) will fail on such data
unless aggregated appropriately. Instead, a cluster analysis algorithm
may be able to detect the micro-clusters formed by these patterns.[^70]

Three broad categories of anomaly detection techniques exist.[^71]
Unsupervised anomaly detection techniques detect anomalies in an
unlabelled test data set under the assumption that the majority of the
instances in the data set are normal, by looking for instances that seem
to fit the least to the remainder of the data set. Supervised anomaly
detection techniques require a data set that has been labelled as
\"normal\" and \"abnormal\" and involves training a classifier (the key
difference from many other statistical classification problems is the
inherently unbalanced nature of outlier detection). Semi-supervised
anomaly detection techniques construct a model representing normal
behaviour from a given normal training data set and then test the
likelihood of a test instance being generated by the model.

#### Robot learning {#robot_learning}

[Robot learning](Robot_learning "Robot learning"){.wikilink} is inspired
by a multitude of machine learning methods, starting from supervised
learning, reinforcement learning,[^72][^73] and finally
[meta-learning](meta-learning_(computer_science) "meta-learning"){.wikilink}
(e.g. MAML).

#### Association rules {#association_rules}

```{=mediawiki}
{{Main|Association rule learning}}
```
```{=mediawiki}
{{See also|Inductive logic programming}}
```
Association rule learning is a [rule-based machine
learning](rule-based_machine_learning "rule-based machine learning"){.wikilink}
method for discovering relationships between variables in large
databases. It is intended to identify strong rules discovered in
databases using some measure of \"interestingness\".[^74]

Rule-based machine learning is a general term for any machine learning
method that identifies, learns, or evolves \"rules\" to store,
manipulate or apply knowledge. The defining characteristic of a
rule-based machine learning algorithm is the identification and
utilisation of a set of relational rules that collectively represent the
knowledge captured by the system. This is in contrast to other machine
learning algorithms that commonly identify a singular model that can be
universally applied to any instance in order to make a prediction.[^75]
Rule-based machine learning approaches include [learning classifier
systems](learning_classifier_system "learning classifier system"){.wikilink},
association rule learning, and [artificial immune
systems](artificial_immune_system "artificial immune system"){.wikilink}.

Based on the concept of strong rules, [Rakesh
Agrawal](Rakesh_Agrawal_(computer_scientist) "Rakesh Agrawal"){.wikilink},
[Tomasz Imieliński](Tomasz_Imieliński "Tomasz Imieliński"){.wikilink}
and Arun Swami introduced association rules for discovering regularities
between products in large-scale transaction data recorded by
[point-of-sale](point-of-sale "point-of-sale"){.wikilink} (POS) systems
in supermarkets.[^76] For example, the rule
$\{\mathrm{onions, potatoes}\} \Rightarrow \{\mathrm{burger}\}$ found in
the sales data of a supermarket would indicate that if a customer buys
onions and potatoes together, they are likely to also buy hamburger
meat. Such information can be used as the basis for decisions about
marketing activities such as promotional
[pricing](pricing "pricing"){.wikilink} or [product
placements](product_placement "product placement"){.wikilink}. In
addition to [market basket
analysis](market_basket_analysis "market basket analysis"){.wikilink},
association rules are employed today in application areas including [Web
usage mining](Web_usage_mining "Web usage mining"){.wikilink},
[intrusion
detection](intrusion_detection "intrusion detection"){.wikilink},
[continuous
production](continuous_production "continuous production"){.wikilink},
and [bioinformatics](bioinformatics "bioinformatics"){.wikilink}. In
contrast with [sequence
mining](sequence_mining "sequence mining"){.wikilink}, association rule
learning typically does not consider the order of items either within a
transaction or across transactions.

[Learning classifier
systems](Learning_classifier_system "Learning classifier system"){.wikilink}
(LCS) are a family of rule-based machine learning algorithms that
combine a discovery component, typically a [genetic
algorithm](genetic_algorithm "genetic algorithm"){.wikilink}, with a
learning component, performing either [supervised
learning](supervised_learning "supervised learning"){.wikilink},
[reinforcement
learning](reinforcement_learning "reinforcement learning"){.wikilink},
or [unsupervised
learning](unsupervised_learning "unsupervised learning"){.wikilink}.
They seek to identify a set of context-dependent rules that collectively
store and apply knowledge in a
[piecewise](piecewise "piecewise"){.wikilink} manner to make
predictions.[^77]

[Inductive logic
programming](Inductive_logic_programming "Inductive logic programming"){.wikilink}
(ILP) is an approach to rule learning using [logic
programming](logic_programming "logic programming"){.wikilink} as a
uniform representation for input examples, background knowledge, and
hypotheses. Given an encoding of the known background knowledge and a
set of examples represented as a logical database of facts, an ILP
system will derive a hypothesized logic program that
[entails](Entailment "entails"){.wikilink} all positive and no negative
examples. [Inductive
programming](Inductive_programming "Inductive programming"){.wikilink}
is a related field that considers any kind of programming language for
representing hypotheses (and not only logic programming), such as
[functional
programs](Functional_programming "functional programs"){.wikilink}.

Inductive logic programming is particularly useful in
[bioinformatics](bioinformatics "bioinformatics"){.wikilink} and
[natural language
processing](natural_language_processing "natural language processing"){.wikilink}.
[Gordon Plotkin](Gordon_Plotkin "Gordon Plotkin"){.wikilink} and [Ehud
Shapiro](Ehud_Shapiro "Ehud Shapiro"){.wikilink} laid the initial
theoretical foundation for inductive machine learning in a logical
setting.[^78][^79][^80] Shapiro built their first implementation (Model
Inference System) in 1981: a Prolog program that inductively inferred
logic programs from positive and negative examples.[^81] The term
*inductive* here refers to
[philosophical](Inductive_reasoning "philosophical"){.wikilink}
induction, suggesting a theory to explain observed facts, rather than
[mathematical
induction](mathematical_induction "mathematical induction"){.wikilink},
proving a property for all members of a well-ordered set.

## Models

A **`{{vanchor|machine learning model}}`{=mediawiki}** is a type of
[mathematical model](mathematical_model "mathematical model"){.wikilink}
that, once \"trained\" on a given dataset, can be used to make
predictions or classifications on new data. During training, a learning
algorithm iteratively adjusts the model\'s internal parameters to
minimise errors in its predictions.[^82] By extension, the term
\"model\" can refer to several levels of specificity, from a general
class of models and their associated learning algorithms to a fully
trained model with all its internal parameters tuned.[^83]

Various types of models have been used and researched for machine
learning systems, picking the best model for a task is called [model
selection](model_selection "model selection"){.wikilink}.

### Artificial neural networks {#artificial_neural_networks}

```{=mediawiki}
{{Main|Artificial neural network}}
```
```{=mediawiki}
{{See also|Deep learning}}
```
![An artificial neural network is an interconnected group of nodes, akin
to the vast network of [neurons](neuron "neuron"){.wikilink} in a
[brain](brain "brain"){.wikilink}. Here, each circular node represents
an [artificial neuron](artificial_neuron "artificial neuron"){.wikilink}
and an arrow represents a connection from the output of one artificial
neuron to the input of
another.](Colored_neural_network.svg "An artificial neural network is an interconnected group of nodes, akin to the vast network of neurons in a brain. Here, each circular node represents an artificial neuron and an arrow represents a connection from the output of one artificial neuron to the input of another."){width="225"}

Artificial neural networks (ANNs), or
[connectionist](Connectionism "connectionist"){.wikilink} systems, are
computing systems vaguely inspired by the [biological neural
networks](biological_neural_network "biological neural network"){.wikilink}
that constitute animal [brains](brain "brain"){.wikilink}. Such systems
\"learn\" to perform tasks by considering examples, generally without
being programmed with any task-specific rules.

An ANN is a model based on a collection of connected units or nodes
called \"[artificial
neurons](artificial_neuron "artificial neuron"){.wikilink}\", which
loosely model the [neurons](neuron "neuron"){.wikilink} in a biological
brain. Each connection, like the
[synapses](synapse "synapse"){.wikilink} in a biological brain, can
transmit information, a \"signal\", from one artificial neuron to
another. An artificial neuron that receives a signal can process it and
then signal additional artificial neurons connected to it. In common ANN
implementations, the signal at a connection between artificial neurons
is a [real number](real_number "real number"){.wikilink}, and the output
of each artificial neuron is computed by some non-linear function of the
sum of its inputs. The connections between artificial neurons are called
\"edges\". Artificial neurons and edges typically have a
[weight](weight_(mathematics) "weight"){.wikilink} that adjusts as
learning proceeds. The weight increases or decreases the strength of the
signal at a connection. Artificial neurons may have a threshold such
that the signal is only sent if the aggregate signal crosses that
threshold. Typically, artificial neurons are aggregated into layers.
Different layers may perform different kinds of transformations on their
inputs. Signals travel from the first layer (the input layer) to the
last layer (the output layer), possibly after traversing the layers
multiple times.

The original goal of the ANN approach was to solve problems in the same
way that a [human brain](human_brain "human brain"){.wikilink} would.
However, over time, attention moved to performing specific tasks,
leading to deviations from [biology](biology "biology"){.wikilink}.
Artificial neural networks have been used on a variety of tasks,
including [computer
vision](computer_vision "computer vision"){.wikilink}, [speech
recognition](speech_recognition "speech recognition"){.wikilink},
[machine
translation](machine_translation "machine translation"){.wikilink},
[social network](social_network "social network"){.wikilink} filtering,
[playing board and video
games](general_game_playing "playing board and video games"){.wikilink}
and [medical
diagnosis](medical_diagnosis "medical diagnosis"){.wikilink}.

[Deep learning](Deep_learning "Deep learning"){.wikilink} consists of
multiple hidden layers in an artificial neural network. This approach
tries to model the way the human brain processes light and sound into
vision and hearing. Some successful applications of deep learning are
computer vision and speech recognition.[^84]

### Decision trees {#decision_trees}

```{=mediawiki}
{{Main|Decision tree learning}}
```
![A decision tree showing survival probability of passengers on the
[Titanic](Titanic "Titanic"){.wikilink}](Decision_Tree.jpg "A decision tree showing survival probability of passengers on the Titanic"){width="300"}

Decision tree learning uses a [decision
tree](decision_tree "decision tree"){.wikilink} as a [predictive
model](Predictive_modeling "predictive model"){.wikilink} to go from
observations about an item (represented in the branches) to conclusions
about the item\'s target value (represented in the leaves). It is one of
the predictive modelling approaches used in statistics, data mining, and
machine learning. Tree models where the target variable can take a
discrete set of values are called classification trees; in these tree
structures, [leaves](leaf_node "leaves"){.wikilink} represent class
labels, and branches represent
[conjunctions](Logical_conjunction "conjunction"){.wikilink} of features
that lead to those class labels. Decision trees where the target
variable can take continuous values (typically [real
numbers](real_numbers "real numbers"){.wikilink}) are called regression
trees. In decision analysis, a decision tree can be used to visually and
explicitly represent decisions and [decision
making](decision_making "decision making"){.wikilink}. In data mining, a
decision tree describes data, but the resulting classification tree can
be an input for decision-making.

### Random forest regression {#random_forest_regression}

[Random forest
regression](Random_forest "Random forest regression"){.wikilink} (RFR)
falls under the umbrella of decision [tree-based
models](tree-based_models "tree-based models"){.wikilink}. RFR is an
ensemble learning method that builds multiple decision trees and
averages their predictions to improve accuracy and to avoid overfitting.
To build decision trees, RFR uses bootstrapped sampling; for instance,
each decision tree is trained on random data from the training set. This
random selection of RFR for training enables the model to reduce biased
predictions and achieve a higher degree of accuracy. RFR generates
independent decision trees, and it can work on single-output data as
well as multiple regressor tasks. This makes RFR compatible to be use in
various applications.[^85][^86]

### Support-vector machines {#support_vector_machines}

```{=mediawiki}
{{Main|Support-vector machine}}
```
Support-vector machines (SVMs), also known as support-vector networks,
are a set of related [supervised
learning](supervised_learning "supervised learning"){.wikilink} methods
used for classification and regression. Given a set of training
examples, each marked as belonging to one of two categories, an SVM
training algorithm builds a model that predicts whether a new example
falls into one category.[^87] An SVM training algorithm is a
non-[probabilistic](probabilistic_classification "probabilistic"){.wikilink},
[binary](binary_classifier "binary"){.wikilink}, [linear
classifier](linear_classifier "linear classifier"){.wikilink}, although
methods such as [Platt
scaling](Platt_scaling "Platt scaling"){.wikilink} exist to use SVM in a
probabilistic classification setting. In addition to performing linear
classification, SVMs can efficiently perform a non-linear classification
using what is called the [kernel
trick](kernel_trick "kernel trick"){.wikilink}, implicitly mapping their
inputs into high-dimensional feature spaces.

### Regression analysis {#regression_analysis}

```{=mediawiki}
{{Main|Regression analysis}}
```
[thumb\|upright=1.3\|Illustration of linear regression on a data
set](Image:Linear_regression.svg "thumb|upright=1.3|Illustration of linear regression on a data set"){.wikilink}

Regression analysis encompasses a large variety of statistical methods
to estimate the relationship between input variables and their
associated features. Its most common form is [linear
regression](linear_regression "linear regression"){.wikilink}, where a
single line is drawn to best fit the given data according to a
mathematical criterion such as [ordinary least
squares](ordinary_least_squares "ordinary least squares"){.wikilink}.
The latter is often extended by
[regularisation](regularization_(mathematics) "regularisation"){.wikilink}
methods to mitigate overfitting and bias, as in [ridge
regression](ridge_regression "ridge regression"){.wikilink}. When
dealing with non-linear problems, go-to models include [polynomial
regression](polynomial_regression "polynomial regression"){.wikilink}
(for example, used for trendline fitting in Microsoft Excel[^88]),
[logistic
regression](logistic_regression "logistic regression"){.wikilink} (often
used in [statistical
classification](statistical_classification "statistical classification"){.wikilink})
or even [kernel
regression](kernel_regression "kernel regression"){.wikilink}, which
introduces non-linearity by taking advantage of the [kernel
trick](kernel_trick "kernel trick"){.wikilink} to implicitly map input
variables to higher-dimensional space.

[Multivariate linear
regression](General_linear_model "Multivariate linear regression"){.wikilink}
extends the concept of linear regression to handle multiple dependent
variables simultaneously. This approach estimates the relationships
between a set of input variables and several output variables by fitting
a
[multidimensional](Multidimensional_system "multidimensional"){.wikilink}
linear model. It is particularly useful in scenarios where outputs are
interdependent or share underlying patterns, such as predicting multiple
economic indicators or reconstructing images,[^89] which are inherently
multi-dimensional.

### Bayesian networks {#bayesian_networks}

```{=mediawiki}
{{Main|Bayesian network}}
```
![A simple Bayesian network. Rain influences whether the sprinkler is
activated, and both rain and the sprinkler influence whether the grass
is
wet.](SimpleBayesNetNodes.svg "A simple Bayesian network. Rain influences whether the sprinkler is activated, and both rain and the sprinkler influence whether the grass is wet.")

A Bayesian network, belief network, or directed acyclic graphical model
is a probabilistic [graphical
model](graphical_model "graphical model"){.wikilink} that represents a
set of [random
variables](random_variables "random variables"){.wikilink} and their
[conditional
independence](conditional_independence "conditional independence"){.wikilink}
with a [directed acyclic
graph](directed_acyclic_graph "directed acyclic graph"){.wikilink}
(DAG). For example, a Bayesian network could represent the probabilistic
relationships between diseases and symptoms. Given symptoms, the network
can be used to compute the probabilities of the presence of various
diseases. Efficient algorithms exist that perform
[inference](Bayesian_inference "inference"){.wikilink} and learning.
Bayesian networks that model sequences of variables, like [speech
signals](speech_recognition "speech signals"){.wikilink} or [protein
sequences](peptide_sequence "protein sequences"){.wikilink}, are called
[dynamic Bayesian
networks](dynamic_Bayesian_network "dynamic Bayesian network"){.wikilink}.
Generalisations of Bayesian networks that can represent and solve
decision problems under uncertainty are called [influence
diagrams](influence_diagram "influence diagram"){.wikilink}.

### Gaussian processes {#gaussian_processes}

```{=mediawiki}
{{Main|Gaussian processes}}
```
![An example of Gaussian Process Regression (prediction) compared with
other regression
models[^90]](Regressions_sine_demo.svg "An example of Gaussian Process Regression (prediction) compared with other regression models")

A Gaussian process is a [stochastic
process](stochastic_process "stochastic process"){.wikilink} in which
every finite collection of the random variables in the process has a
[multivariate normal
distribution](multivariate_normal_distribution "multivariate normal distribution"){.wikilink},
and it relies on a pre-defined [covariance
function](covariance_function "covariance function"){.wikilink}, or
kernel, that models how pairs of points relate to each other depending
on their locations.

Given a set of observed points, or input--output examples, the
distribution of the (unobserved) output of a new point as a function of
its input data can be directly computed by looking at the observed
points and the covariances between those points and the new, unobserved
point.

Gaussian processes are popular surrogate models in [Bayesian
optimisation](Bayesian_optimisation "Bayesian optimisation"){.wikilink}
used to do [hyperparameter
optimisation](hyperparameter_optimisation "hyperparameter optimisation"){.wikilink}.

### Genetic algorithms {#genetic_algorithms}

```{=mediawiki}
{{Main|Genetic algorithm}}
```
A genetic algorithm (GA) is a [search
algorithm](search_algorithm "search algorithm"){.wikilink} and
[heuristic](heuristic_(computer_science) "heuristic"){.wikilink}
technique that mimics the process of [natural
selection](natural_selection "natural selection"){.wikilink}, using
methods such as
[mutation](Mutation_(genetic_algorithm) "mutation"){.wikilink} and
[crossover](Crossover_(genetic_algorithm) "crossover"){.wikilink} to
generate new
[genotypes](Chromosome_(genetic_algorithm) "genotype"){.wikilink} in the
hope of finding good solutions to a given problem. In machine learning,
genetic algorithms were used in the 1980s and 1990s.[^92][^93]
Conversely, machine learning techniques have been used to improve the
performance of genetic and [evolutionary
algorithms](evolutionary_algorithm "evolutionary algorithm"){.wikilink}.[^94]

### Belief functions {#belief_functions}

```{=mediawiki}
{{Main|Dempster–Shafer theory}}
```
The theory of belief functions, also referred to as evidence theory or
Dempster--Shafer theory, is a general framework for reasoning with
uncertainty, with understood connections to other frameworks such as
[probability](probability "probability"){.wikilink},
[possibility](Possibility_theory "possibility"){.wikilink} and
[imprecise probability
theories](Imprecise_probability "imprecise probability theories"){.wikilink}.
These theoretical frameworks can be thought of as a kind of learner and
have some analogous properties of how evidence is combined (e.g.,
Dempster\'s rule of combination), just like how in a
[pmf](Probability_mass_function "pmf"){.wikilink}-based Bayesian
approach would combine probabilities.[^95] However, there are many
caveats to these beliefs functions when compared to Bayesian approaches
to incorporate ignorance and [uncertainty
quantification](uncertainty_quantification "uncertainty quantification"){.wikilink}.
These belief function approaches that are implemented within the machine
learning domain typically leverage a fusion approach of various
[ensemble methods](ensemble_methods "ensemble methods"){.wikilink} to
better handle the learner\'s [decision
boundary](decision_boundary "decision boundary"){.wikilink}, low
samples, and ambiguous class issues that standard machine learning
approach tend to have difficulty resolving.[^96][^97] However, the
computational complexity of these algorithms is dependent on the number
of propositions (classes), and can lead to a much higher computation
time when compared to other machine learning approaches.

### Rule-based models {#rule_based_models}

```{=mediawiki}
{{Main|Rule-based machine learning}}
```
Rule-based machine learning (RBML) is a branch of machine learning that
automatically discovers and learns \'rules\' from data. It provides
interpretable models, making it useful for decision-making in fields
like healthcare, fraud detection, and cybersecurity. Key RBML techniques
includes [learning classifier
systems](learning_classifier_system "learning classifier system"){.wikilink},[^98]
[association rule
learning](association_rule_learning "association rule learning"){.wikilink},[^99]
[artificial immune
systems](artificial_immune_system "artificial immune system"){.wikilink},[^100]
and other similar models. These methods extract patterns from data and
evolve rules over time.

### Training models {#training_models}

Typically, machine learning models require a high quantity of reliable
data to perform accurate predictions. When training a machine learning
model, machine learning engineers need to target and collect a large and
representative [sample](Sample_(statistics) "sample"){.wikilink} of
data. Data from the training set can be as varied as a [corpus of
text](corpus_of_text "corpus of text"){.wikilink}, a collection of
images, [sensor](sensor "sensor"){.wikilink} data, and data collected
from individual users of a service.
[Overfitting](Overfitting "Overfitting"){.wikilink} is something to
watch out for when training a machine learning model. Trained models
derived from biased or non-evaluated data can result in skewed or
undesired predictions. Biased models may result in detrimental outcomes,
thereby furthering the negative impacts on society or objectives.
[Algorithmic bias](Algorithmic_bias "Algorithmic bias"){.wikilink} is a
potential result of data not being fully prepared for training. Machine
learning ethics is becoming a field of study and, notably, becoming
integrated within machine learning engineering teams.

#### Federated learning {#federated_learning}

```{=mediawiki}
{{Main|Federated learning}}
```
Federated learning is an adapted form of [distributed artificial
intelligence](distributed_artificial_intelligence "distributed artificial intelligence"){.wikilink}
to train machine learning models that decentralises the training
process, allowing for users\' privacy to be maintained by not needing to
send their data to a centralised server. This also increases efficiency
by decentralising the training process to many devices. For example,
[Gboard](Gboard "Gboard"){.wikilink} uses federated machine learning to
train search query prediction models on users\' mobile phones without
having to send individual searches back to
[Google](Google "Google"){.wikilink}.[^101]

## Applications

There are many applications for machine learning, including:
`{{cols|colwidth=21em}}`{=mediawiki}

- [Agriculture](Precision_agriculture "Agriculture"){.wikilink}
- [Anatomy](Computational_anatomy "Anatomy"){.wikilink}
- [Adaptive website](Adaptive_website "Adaptive website"){.wikilink}
- [Affective
  computing](Affective_computing "Affective computing"){.wikilink}
- [Astronomy](Astroinformatics "Astronomy"){.wikilink}
- [Automated
  decision-making](Automated_decision-making "Automated decision-making"){.wikilink}
- [Banking](Banking "Banking"){.wikilink}
- [Behaviorism](Behaviorism "Behaviorism"){.wikilink}
- [Bioinformatics](Bioinformatics "Bioinformatics"){.wikilink}
- [Brain--machine
  interfaces](Brain–computer_interface "Brain–machine interfaces"){.wikilink}
- [Cheminformatics](Cheminformatics "Cheminformatics"){.wikilink}
- [Citizen Science](Citizen_Science "Citizen Science"){.wikilink}
- [Climate Science](Climate_Science "Climate Science"){.wikilink}
- [Computer networks](Network_simulation "Computer networks"){.wikilink}
- [Computer vision](Computer_vision "Computer vision"){.wikilink}
- [Credit-card fraud](Credit-card_fraud "Credit-card fraud"){.wikilink}
  detection
- [Data quality](Data_quality "Data quality"){.wikilink}
- [DNA sequence](DNA_sequence "DNA sequence"){.wikilink} classification
- [Economics](Computational_economics "Economics"){.wikilink}
- [Financial data
  analysis](Data_analysis "Financial data analysis"){.wikilink}[^102]

Because of such challenges, the effective use of machine learning may
take longer to be adopted in other domains.[^103] Concern for
[fairness](Fairness_(machine_learning) "fairness"){.wikilink} in machine
learning, that is, reducing bias in machine learning and propelling its
use for human good, is increasingly expressed by artificial intelligence
scientists, including [Fei-Fei Li](Fei-Fei_Li "Fei-Fei Li"){.wikilink},
who said that \"\[t\]here\'s nothing artificial about AI. It\'s inspired
by people, it\'s created by people, and---most importantly---it impacts
people. It is a powerful tool we are only just beginning to understand,
and that is a profound responsibility.\"[^104]

### Financial incentives {#financial_incentives}

There are concerns among health care professionals that these systems
might not be designed in the public\'s interest but as income-generating
machines. This is especially true in the United States, where there is a
long-standing ethical dilemma of improving health care, but also
increasing profits. For example, the algorithms could be designed to
provide patients with unnecessary tests or medication in which the
algorithm\'s proprietary owners hold stakes. There is potential for
machine learning in health care to provide professionals with an
additional tool to diagnose, medicate, and plan recovery paths for
patients, but this requires these biases to be mitigated.[^105]

## Hardware

Since the 2010s, advances in both machine learning algorithms and
computer hardware have led to more efficient methods for training [deep
neural networks](deep_neural_network "deep neural network"){.wikilink}
(a particular narrow subdomain of machine learning) that contain many
layers of nonlinear hidden units.[^106] By 2019, graphics processing
units ([GPUs](GPU "GPU"){.wikilink}), often with AI-specific
enhancements, had displaced CPUs as the dominant method of training
large-scale commercial cloud AI.[^107]
[OpenAI](OpenAI "OpenAI"){.wikilink} estimated the hardware compute used
in the largest deep learning projects from
[AlexNet](AlexNet "AlexNet"){.wikilink} (2012) to
[AlphaZero](AlphaZero "AlphaZero"){.wikilink} (2017), and found a
300,000-fold increase in the amount of compute required, with a
doubling-time trendline of 3.4 months.[^108][^109]

### Tensor Processing Units (TPUs) {#tensor_processing_units_tpus}

[Tensor Processing Units
(TPUs)](Tensor_Processing_Unit "Tensor Processing Units (TPUs)"){.wikilink}
are specialised hardware accelerators developed by
[Google](Google "Google"){.wikilink} specifically for machine learning
workloads. Unlike general-purpose
[GPUs](Graphics_processing_unit "GPUs"){.wikilink} and
[FPGAs](Field-programmable_gate_array "FPGAs"){.wikilink}, TPUs are
optimised for tensor computations, making them particularly efficient
for deep learning tasks such as training and inference. They are widely
used in Google Cloud AI services and large-scale machine learning models
like Google\'s DeepMind AlphaFold and large language models. TPUs
leverage matrix multiplication units and high-bandwidth memory to
accelerate computations while maintaining energy efficiency.[^110] Since
their introduction in 2016, TPUs have become a key component of AI
infrastructure, especially in cloud-based environments.

### Neuromorphic computing {#neuromorphic_computing}

[Neuromorphic
computing](Neuromorphic_computing "Neuromorphic computing"){.wikilink}
refers to a class of computing systems designed to emulate the structure
and functionality of biological neural networks. These systems may be
implemented through software-based simulations on conventional hardware
or through specialised hardware architectures.[^111]

#### Physical neural networks {#physical_neural_networks}

A [physical neural
network](physical_neural_network "physical neural network"){.wikilink}
is a specific type of neuromorphic hardware that relies on electrically
adjustable materials, such as memristors, to emulate the function of
[neural synapses](chemical_synapse "neural synapses"){.wikilink}. The
term \"physical neural network\" highlights the use of physical hardware
for computation, as opposed to software-based implementations. It
broadly refers to artificial neural networks that use materials with
adjustable resistance to replicate neural synapses.[^112][^113]

### Embedded machine learning {#embedded_machine_learning}

Embedded machine learning is a sub-field of machine learning where
models are deployed on [embedded
systems](embedded_systems "embedded systems"){.wikilink} with limited
computing resources, such as [wearable
computers](wearable_computer "wearable computer"){.wikilink}, [edge
devices](edge_device "edge device"){.wikilink} and
[microcontrollers](microcontrollers "microcontrollers"){.wikilink}.[^114][^115][^116][^117]
Running models directly on these devices eliminates the need to transfer
and store data on cloud servers for further processing, thereby reducing
the risk of data breaches, privacy leaks and theft of intellectual
property, personal data and business secrets. Embedded machine learning
can be achieved through various techniques, such as [hardware
acceleration](hardware_acceleration "hardware acceleration"){.wikilink},[^118][^119]
[approximate
computing](approximate_computing "approximate computing"){.wikilink},[^120]
and model optimisation.[^121][^122] Common optimisation techniques
include
[pruning](Pruning_(artificial_neural_network) "pruning"){.wikilink},
[quantisation](Model_compression#Quantization "quantisation"){.wikilink},
[knowledge
distillation](knowledge_distillation "knowledge distillation"){.wikilink},
low-rank factorisation, network architecture search, and parameter
sharing.

## Software

[Software suites](Software_suite "Software suite"){.wikilink} containing
a variety of machine learning algorithms include the following:

### Free and open-source software`{{anchor|Open-source_software}}`{=mediawiki} {#free_and_open_source_software}

```{=mediawiki}
{{See also|Lists of open-source artificial intelligence software}}
```
```{=mediawiki}
{{Div col|colwidth=18em}}
```
- [Caffe](Caffe_(software) "Caffe"){.wikilink}
- [Deeplearning4j](Deeplearning4j "Deeplearning4j"){.wikilink}
- [DeepSpeed](DeepSpeed "DeepSpeed"){.wikilink}
- [ELKI](ELKI "ELKI"){.wikilink}
- [Google JAX](Google_JAX "Google JAX"){.wikilink}
- [Infer.NET](Infer.NET "Infer.NET"){.wikilink}
- [JASP](JASP "JASP"){.wikilink}
- [Jubatus](Jubatus "Jubatus"){.wikilink}
- [Keras](Keras "Keras"){.wikilink}
- [Kubeflow](Kubeflow "Kubeflow"){.wikilink}
- [LightGBM](LightGBM "LightGBM"){.wikilink}
- [Mahout](Apache_Mahout "Mahout"){.wikilink}
- [Mallet](Mallet_(software_project) "Mallet"){.wikilink}
- [Microsoft Cognitive
  Toolkit](Microsoft_Cognitive_Toolkit "Microsoft Cognitive Toolkit"){.wikilink}
- [ML.NET](ML.NET "ML.NET"){.wikilink}
- [mlpack](mlpack "mlpack"){.wikilink}
- [MXNet](MXNet "MXNet"){.wikilink}
- [OpenNN](OpenNN "OpenNN"){.wikilink}
- [Orange](Orange_(software) "Orange"){.wikilink}
- [pandas (software)](pandas_(software) "pandas (software)"){.wikilink}
- [ROOT](ROOT "ROOT"){.wikilink} (TMVA with ROOT)
- [scikit-learn](scikit-learn "scikit-learn"){.wikilink}
- [Shogun](Shogun_(toolbox) "Shogun"){.wikilink}
- [Spark
  MLlib](Apache_Spark#MLlib_Machine_Learning_Library "Spark MLlib"){.wikilink}
- [SystemML](Apache_SystemML "SystemML"){.wikilink}
- [Theano](Theano_(software) "Theano"){.wikilink}
- [TensorFlow](TensorFlow "TensorFlow"){.wikilink}
- [Torch](Torch_(machine_learning) "Torch"){.wikilink} /
  [PyTorch](PyTorch "PyTorch"){.wikilink}
- [Weka](Weka_(machine_learning) "Weka"){.wikilink} /
  [MOA](MOA_(Massive_Online_Analysis) "MOA"){.wikilink}
- [XGBoost](XGBoost "XGBoost"){.wikilink}
- [Yooreeka](Yooreeka "Yooreeka"){.wikilink}

```{=mediawiki}
{{Div col end}}
```
### Proprietary software with free and open-source editions {#proprietary_software_with_free_and_open_source_editions}

- [KNIME](KNIME "KNIME"){.wikilink}
- [RapidMiner](RapidMiner "RapidMiner"){.wikilink}

### Proprietary software {#proprietary_software}

```{=mediawiki}
{{Div col|colwidth=18em}}
```
- [Amazon Machine
  Learning](Amazon_Machine_Learning "Amazon Machine Learning"){.wikilink}
- [Angoss](Angoss "Angoss"){.wikilink} KnowledgeSTUDIO
- [Azure Machine
  Learning](Azure_Machine_Learning "Azure Machine Learning"){.wikilink}
- [IBM Watson Studio](IBM_Watson_Studio "IBM Watson Studio"){.wikilink}
- [Google Cloud Vertex
  AI](Google_Cloud_Platform#Cloud_AI "Google Cloud Vertex AI"){.wikilink}
- [Google Prediction
  API](Google_APIs "Google Prediction API"){.wikilink}
- [IBM SPSS Modeller](SPSS_Modeler "IBM SPSS Modeller"){.wikilink}
- [KXEN Modeller](KXEN_Inc. "KXEN Modeller"){.wikilink}
- [LIONsolver](LIONsolver "LIONsolver"){.wikilink}
- [Mathematica](Mathematica "Mathematica"){.wikilink}
- [MATLAB](MATLAB "MATLAB"){.wikilink}
- [Neural Designer](Neural_Designer "Neural Designer"){.wikilink}
- [NeuroSolutions](NeuroSolutions "NeuroSolutions"){.wikilink}
- [Oracle Data
  Mining](Oracle_Data_Mining "Oracle Data Mining"){.wikilink}
- [Oracle AI Platform Cloud
  Service](Oracle_Cloud#Platform_as_a_Service_(PaaS) "Oracle AI Platform Cloud Service"){.wikilink}
- [PolyAnalyst](PolyAnalyst "PolyAnalyst"){.wikilink}
- [RCASE](RCASE "RCASE"){.wikilink}
- [SAS Enterprise
  Miner](SAS_(software)#Components "SAS Enterprise Miner"){.wikilink}
- [SequenceL](SequenceL "SequenceL"){.wikilink}
- [Splunk](Splunk "Splunk"){.wikilink}
- [STATISTICA](STATISTICA "STATISTICA"){.wikilink} Data Miner

```{=mediawiki}
{{Div col end}}
```
## Journals

- [Journal of Machine Learning
  Research](Journal_of_Machine_Learning_Research "Journal of Machine Learning Research"){.wikilink}
- [Machine
  Learning](Machine_Learning_(journal) "Machine Learning"){.wikilink}
- [Nature Machine
  Intelligence](Nature_Machine_Intelligence "Nature Machine Intelligence"){.wikilink}
- [Neural
  Computation](Neural_Computation_(journal) "Neural Computation"){.wikilink}
- [IEEE Transactions on Pattern Analysis and Machine
  Intelligence](IEEE_Transactions_on_Pattern_Analysis_and_Machine_Intelligence "IEEE Transactions on Pattern Analysis and Machine Intelligence"){.wikilink}

## Conferences

- [AAAI Conference on Artificial
  Intelligence](AAAI_Conference_on_Artificial_Intelligence "AAAI Conference on Artificial Intelligence"){.wikilink}
- [Association for Computational Linguistics
  (**ACL**)](Association_for_Computational_Linguistics "Association for Computational Linguistics (ACL)"){.wikilink}
- [European Conference on Machine Learning and Principles and Practice
  of Knowledge Discovery in Databases (**ECML
  PKDD**)](European_Conference_on_Machine_Learning_and_Principles_and_Practice_of_Knowledge_Discovery_in_Databases "European Conference on Machine Learning and Principles and Practice of Knowledge Discovery in Databases (ECML PKDD)"){.wikilink}
- [International Conference on Computational Intelligence Methods for
  Bioinformatics and Biostatistics
  (**CIBB**)](International_Conference_on_Computational_Intelligence_Methods_for_Bioinformatics_and_Biostatistics "International Conference on Computational Intelligence Methods for Bioinformatics and Biostatistics (CIBB)"){.wikilink}
- [International Conference on Machine Learning
  (**ICML**)](International_Conference_on_Machine_Learning "International Conference on Machine Learning (ICML)"){.wikilink}
- [International Conference on Learning Representations
  (**ICLR**)](International_Conference_on_Learning_Representations "International Conference on Learning Representations (ICLR)"){.wikilink}
- [International Conference on Intelligent Robots and Systems
  (**IROS**)](International_Conference_on_Intelligent_Robots_and_Systems "International Conference on Intelligent Robots and Systems (IROS)"){.wikilink}
- [Conference on Knowledge Discovery and Data Mining
  (**KDD**)](Conference_on_Knowledge_Discovery_and_Data_Mining "Conference on Knowledge Discovery and Data Mining (KDD)"){.wikilink}
- [Conference on Neural Information Processing Systems
  (**NeurIPS**)](Conference_on_Neural_Information_Processing_Systems "Conference on Neural Information Processing Systems (NeurIPS)"){.wikilink}

## See also {#see_also}

- ```{=mediawiki}
  {{annotated link|Automated machine learning}}
  ```

- ```{=mediawiki}
  {{annotated link|Big data}}
  ```

- [Deep learning](Deep_learning "Deep learning"){.wikilink} --- branch
  of ML concerned with [artificial neural
  networks](artificial_neural_network "artificial neural network"){.wikilink}

- ```{=mediawiki}
  {{annotated link|Differentiable programming}}
  ```

- ```{=mediawiki}
  {{annotated link|List of datasets for machine-learning research}}
  ```

- [List of machine learning
  algorithms](Outline_of_machine_learning#Machine_learning_algorithms "List of machine learning algorithms"){.wikilink}
  and [List of algorithms for machine learning and statistical
  classification](List_of_algorithms#Machine_learning_and_statistical_classification "List of algorithms for machine learning and statistical classification"){.wikilink}

- ```{=mediawiki}
  {{annotated link|M-theory (learning framework)}}
  ```

- ```{=mediawiki}
  {{annotated link|Machine unlearning}}
  ```

- [Outline of machine
  learning](Outline_of_machine_learning "Outline of machine learning"){.wikilink}

- ```{=mediawiki}
  {{annotated link|Solomonoff's theory of inductive inference}}
  ```

## References

```{=mediawiki}
{{Reflist|30em}}
```
## Sources

- ```{=mediawiki}
  {{Cite book
  | last = Domingos | first = Pedro | author-link = Pedro Domingos
  | title =  The Master Algorithm: How the Quest for the Ultimate Learning Machine Will Remake Our World
  | date = 22 September 2015
  | publisher = Basic Books
  | isbn = 978-0-465-06570-7
  }}
  ```

- ```{=mediawiki}
  {{Cite book|last=Nilsson|first=Nils|author-link=Nils Nilsson (researcher)|year=1998|title=Artificial Intelligence: A New Synthesis|url=https://archive.org/details/artificialintell0000nils|url-access=registration|publisher=Morgan Kaufmann|isbn=978-1-55860-467-4|access-date=18 November 2019|archive-date=26 July 2020|archive-url=https://web.archive.org/web/20200726131654/https://archive.org/details/artificialintell0000nils|url-status=live}}
  ```

- ```{=mediawiki}
  {{Cite book|first1=David|last1=Poole|first2=Alan|last2=Mackworth|author2-link=Alan Mackworth|first3=Randy|last3=Goebel|year=1998|title=Computational Intelligence: A Logical Approach|publisher=Oxford University Press|location=New York|isbn=978-0-19-510270-3|url=https://archive.org/details/computationalint00pool|access-date=22 August 2020|archive-date=26 July 2020|archive-url=https://web.archive.org/web/20200726131436/https://archive.org/details/computationalint00pool|url-status=live}}
  ```

- ```{=mediawiki}
  {{Russell Norvig 2003}}
  ```
  .

## Further reading {#further_reading}

```{=mediawiki}
{{refbegin|30em}}
```
- Alpaydin, Ethem (2020). *Introduction to Machine Learning*, (4th
  edition) MIT Press, `{{ISBN|9780262043793}}`{=mediawiki}.
- [Bishop,
  Christopher](Christopher_Bishop "Bishop, Christopher"){.wikilink}
  (1995). *Neural Networks for Pattern Recognition*, Oxford University
  Press. `{{ISBN|0-19-853864-2}}`{=mediawiki}.
- Bishop, Christopher (2006) *Pattern Recognition and Machine Learning*,
  Springer. `{{ISBN|978-0-387-31073-2}}`{=mediawiki}
- [Domingos, Pedro](Pedro_Domingos "Domingos, Pedro"){.wikilink}
  (September 2015), *[The Master
  Algorithm](The_Master_Algorithm "The Master Algorithm"){.wikilink}*,
  Basic Books, `{{ISBN|978-0-465-06570-7}}`{=mediawiki}
- [Duda, Richard O.](Richard_O._Duda "Duda, Richard O."){.wikilink};
  [Hart, Peter E.](Peter_E._Hart "Hart, Peter E."){.wikilink}; Stork,
  David G. (2001) *Pattern classification* (2nd edition), Wiley, New
  York, `{{ISBN|0-471-05669-3}}`{=mediawiki}.
- [Hastie, Trevor](Trevor_Hastie "Hastie, Trevor"){.wikilink};
  [Tibshirani,
  Robert](Robert_Tibshirani "Tibshirani, Robert"){.wikilink} &
  [Friedman, Jerome
  H.](Jerome_H._Friedman "Friedman, Jerome H."){.wikilink} (2009) *The
  Elements of Statistical Learning*, Springer.
  `{{doi|10.1007/978-0-387-84858-7}}`{=mediawiki}
  `{{ISBN|0-387-95284-5}}`{=mediawiki}.
- [MacKay, David J.
  C.](David_J._C._MacKay "MacKay, David J. C."){.wikilink} *Information
  Theory, Inference, and Learning Algorithms* Cambridge: Cambridge
  University Press, 2003. `{{ISBN|0-521-64298-1}}`{=mediawiki}
- Murphy, Kevin P. (2021). *[Probabilistic Machine Learning: An
  Introduction](https://probml.github.io/pml-book/book1.html)
  `{{Webarchive|url=https://web.archive.org/web/20210411153246/https://probml.github.io/pml-book/book1.html |date=11 April 2021 }}`{=mediawiki}*,
  MIT Press.
- Nilsson, Nils J. (2015) *[Introduction to Machine
  Learning](https://ai.stanford.edu/people/nilsson/mlbook.html)
  `{{Webarchive|url=https://web.archive.org/web/20190816182600/http://ai.stanford.edu/people/nilsson/mlbook.html |date=16 August 2019 }}`{=mediawiki}*.
- Russell, Stuart & Norvig, Peter (2020). *Artificial Intelligence -- A
  Modern Approach*. (4th edition) Pearson,
  `{{ISBN|978-0134610993}}`{=mediawiki}.
- [Solomonoff, Ray](Ray_Solomonoff "Solomonoff, Ray"){.wikilink}, (1956)
  *[An Inductive Inference
  Machine](http://world.std.com/~rjs/indinf56.pdf)
  `{{Webarchive|url=https://web.archive.org/web/20110426161749/http://world.std.com/~rjs/indinf56.pdf |date=26 April 2011 }}`{=mediawiki}*
  A privately circulated report from the 1956 [Dartmouth Summer Research
  Conference on
  AI](Dartmouth_workshop "Dartmouth Summer Research Conference on AI"){.wikilink}.
- Witten, Ian H. & Frank, Eibe (2011). *[Data Mining: Practical machine
  learning tools and
  techniques](https://www.sciencedirect.com/book/9780123748560)* Morgan
  Kaufmann, 664pp., `{{ISBN|978-0-12-374856-0}}`{=mediawiki}.

```{=mediawiki}
{{Refend}}
```
## External links {#external_links}

- [International Machine Learning
  Society](https://web.archive.org/web/20171230081341/http://machinelearning.org/)
- [mloss](https://mloss.org/) is an academic database of open-source
  machine learning software.

```{=mediawiki}
{{Artificial intelligence navbox}}
```
```{=mediawiki}
{{Computer science}}
```
```{=mediawiki}
{{Subject bar|portal1=Computer programming|portal2=Mathematics|portal3=Systems science|portal4=Technology|commons=y|q=y|wikt=machine learning|b=y|u=y|d=y}}
```
```{=mediawiki}
{{Authority control}}
```
[ ](Category:Machine_learning " "){.wikilink}
[Category:Cybernetics](Category:Cybernetics "Category:Cybernetics"){.wikilink}
[Category:Learning](Category:Learning "Category:Learning"){.wikilink}
[Category:Definition](Category:Definition "Category:Definition"){.wikilink}
[Category:Data
science](Category:Data_science "Category:Data science"){.wikilink}