# PESTO
PESTO - Parallel Execution Simulation Tool - was developed at AIT-IES with the purpose of **executing simulations in parallel** distributed on multiple computers coordinated through one main computer (in the following refered to as master).

**PESTO** was written in [**Python 3**](https://www.python.org/download/releases/3.0/) for **Windows** and uses [**PsExec**](https://docs.microsoft.com/en-us/sysinternals/downloads/psexec) (and [**PsKill**](https://docs.microsoft.com/en-us/sysinternals/downloads/pskill)) from [**PsTools**](https://docs.microsoft.com/en-us/sysinternals/downloads/pstools)

**PsTools** has to be ran by the Administrator account, not only an user with administrator rights but the actual Administrator account. The Administrator account must therefore be activated and access to it is a main requirement to run **PESTO**.

Loading resources and saving results happens through a shared drive. The client computers will be connected to this shared drive by **PESTO**.

For further information see: [PESTO wiki](https://github.com/AIT-IES/PESTO/wiki)
