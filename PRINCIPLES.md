# Principles

This project is a job-hunt tool, but the code is only the surface. Underneath it
are a few ideas about how to think, what the tool is really for, and how to write
code that other people can read. This page records those ideas so the reasoning
survives even when the details change.

## Thinking from first principles

First-principles thinking means stripping a problem down to the things that are
true on their own, and then building back up from there. It is the opposite of
reasoning by resemblance, where you copy what a similar project did without asking
whether it fits.

Described by resemblance, this project is "a job scraper." That description hides
more than it reveals. Four things are actually true here, and each one shapes the
design.

The first truth is that jobs are not scarce, but relevant jobs are. Dublin has
thousands of openings and there is one person searching, with limited hours and a
hard requirement to be able to work here legally. The tool exists to turn a flood
of listings into the few worth a real application. The product is filtered signal,
not a list of jobs.

The second truth is that the most valuable fact about a job is never written down.
No advert says "this employer will support a work permit and this role qualifies
for one." That has to be worked out from salary, job title, the employer's history,
and the language of the description. This is the reason the tool needs to reason
about text at all, rather than run a simple database filter.

The third truth is that data from the outside world is messy, repeated, and it goes
stale. The same job appears on several sites. The word "Dublin" also matches Dublin,
California. Fields go missing and adverts expire. This is not a set of bugs to
remove. It is the nature of the material, and the tool has to assume it.

The fourth truth is that you can only act on data you trust. Trust is not a feeling.
It is earned by checking data at the point where it enters the system. That is why
every job is validated the moment it arrives, before anything downstream depends
on it.

Put those four truths together and the real description appears. This is a tool for
making one high-stakes decision under scarcity, uncertainty, and messy information.
That sentence, not "job scraper," is what the code is built to serve.

## Seeing it as a system

Once the ground truths are clear, the next step is to see how they fit together.
A system is made of things that accumulate, things that flow, loops that feed back
on themselves, and a single point that limits the whole.

The thing that accumulates is the table of stored jobs. Everything else exists to
fill it, update it, or clear it out. Seeing the table this way is why saving the
same job twice must never create two rows. A store you cannot trust to hold each
job once is a store you cannot build anything on.

The flows are the stages of work: fetch the jobs, convert them to one format, store
them, enrich them with judgement, and present them. The stages are deliberately
ordered from cheap and simple to expensive and clever. Fetching is cheap. Asking a
language model whether an employer is likely to support a permit is expensive. A
sound design does the cheap filtering first, so the expensive stage only ever looks
at what survived.

The feedback loop is the part that decides whether a job is worth pursuing. It runs
in three levels of growing cost. Plain rules come first, a language model comes
second for the cases the rules cannot settle, and a trained model comes last, much
later. The order matters and cannot be reversed. A trained model needs examples to
learn from, and those examples only exist once the earlier levels have been running
and producing judgements to correct. The system has to run before it can get smart.
Building the trained model first would be building a mind with no past to learn from.

The limiting point is the quality of the permit judgement. It is not speed, and it
is not the number of job sources. Everything else is in service of that one call
being trustworthy. Adding a tenth source does not help if the tool still cannot tell
which of those jobs can lead to a work permit. When it is unclear what to build
next, the test is simple. Does this sharpen the permit judgement, or does it only
move listings around.

## What we are building

The tool is designed for a specific situation. The person searching is a graduate on
a Stamp 1G permit. The Stamp 1G, also called the Third Level Graduate Programme, lets
a non-European graduate of an Irish university stay and work in Ireland for up to two
years without an employer needing to sponsor them first. That single fact reshapes
the whole problem.

It means the goal was never "find employers who sponsor from day one." The goal is to
find a role that can turn into a work permit before the two-year window closes. A
work permit here means the Critical Skills Employment Permit or the General
Employment Permit, each of which has its own salary floor and its own list of
eligible occupations. Because the graduate already has the right to work, an advert
that says nothing about visas is often a good sign rather than a warning.

Three separate questions follow, and the tool must keep them apart instead of
blending them into one muddled answer.

The first is the question of viability. Could anyone on a permit take this job, or
convert it into a permit later? This depends on the salary, the occupation, and the
employer.

The second is the question of fit. Could this particular person, a junior, take this
job? The target is a band of roles that runs from internships and graduate
programmes through junior and entry-level positions. A senior role that demands four
years of experience should rank low even when it is perfectly viable on paper.

The third is the question of timing. Given how much of the two-year window is left,
is this the right kind of role to chase now? Early on, it makes sense to explore
broadly and build experience. Later, the search has to narrow to roles with a clear
and confident path to a permit, because there is no longer time to bet wrong.

Two principles guide how the person interacts with the tool.

The first is to ask for very little input. The right input is not the smallest amount
of typing, but the few facts that change the outcome the most. The person supplies
their permit basis, their level of seniority, their field, and how far they are
willing to travel. They also set a small number of controls they can change over
time: how much of the graduate window remains, whether they want only immediate
sponsors or are open to roles that can convert later, and how confident a judgement
must be before it is shown. The tool works out everything else. The person never
types a salary figure or an occupation code.

The second principle is that confidence is a control the person holds, not a rule
baked into the tool. Every judgement about a permit is a probability with the
evidence attached, never a plain yes or no. A high confidence setting shows only the
near-certain matches, which are few but rarely a waste of time. A low setting shows
everything plausible, which is more to read but misses nothing. The tool stays
honest about its own doubt, and the person decides how much of that doubt to tolerate
on any given day.

Stated plainly, the tool takes a handful of facts and a few controls, watches every
Dublin role in the field, and shows the junior-level ones that the person could
plausibly get and could legally hold. The results are ranked by how well they fit and
how likely they are to lead to a permit, each shown with its evidence, and filtered
by confidence and by how much of the graduate window is left.

## Writing code that stays readable

The same habit of thinking applies to the code itself. Naming the smallest true
steps of a line is first-principles thinking at the scale of a single line, and
keeping the parts of the system apart is systems thinking at the scale of a file.

Readable code is not the simplest possible code, and it is not the cleverest. It is
code whose intent is clear to the person reading it. Consider one line written three
ways. The first packs four operations together with no names, and the reader has to
unpick it. The second avoids the hard ideas but grows noisy and easy to break. The
third does exactly what the first does, but gives each step a name, so the line reads
almost like a sentence. The third is the one to aim for. The beauty comes from naming
the steps, not from removing what the code can do.

A few habits follow from this.

Code is read far more often than it is written, so it should be written for the
person reading it later, who is often its own author months on.

Good names do work that comments cannot. A well-named value explains itself and
removes the need for a note beside it.

One style should be spoken across the whole project. A file that counts a loop one
way while the next file counts it another way reads as though two people wrote it who
never spoke. Consistency is itself a kind of clarity.

Comments should explain why, not what. The code already states what it does. A
comment earns its place by recording a decision the code cannot show on its own.

The messy work of talking to the outside world should be kept apart from the clean
work of logic. Fetching data, validating it, and reshaping it are separate stages
for a reason. Keeping them separate is the habit that matters most in this kind of
work.

Finally, a hard-to-read line is often not a bad line. It is a line written above the
reader's current vocabulary. The cure is to learn the idiom and then use it well,
not to write below your own level forever.

## The path so far and ahead

The groundwork is done. The project has a clean layout, a Python environment, a
database, and a jobs table.

The current stage pulls real Dublin jobs from job-search interfaces that cover
Ireland, beginning with Jooble. Jobs are fetched with paging and polite pauses, then
validated into typed models so that bad data is caught as it arrives. The next step
in this stage is to convert each job into one shared format and store it without
creating duplicates, and then to add a second source behind the same interface.

After that comes the work of reading company hiring systems and removing duplicate
listings, then the heart of the project: using a language model to judge each job for
its permit prospects and its fit. Later stages widen the net to job boards that
publish only as web pages, to sites that need a real browser, and finally to running
the whole thing on a schedule with a small page to search the results.

The shape of the whole effort is steady. Each stage removes one kind of noise, a
wrong location, a broken format, a duplicate, an unsuitable role, an employer who
cannot help, until what remains is small enough for one person to act on with
confidence.
