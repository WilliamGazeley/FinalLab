Plugins follow the naming convention: PluginType_PluginName.py

PluginTypes.csv must be updated if new types of plugins are added.

Types of plugins:

ActivationFunc
    Contains one function, "Func".
    eg. ActivationFunc_sigmoid.py contains func 'Func(x)' and the derivative of func 'FuncPrime(x)'
    
ErrorFunc
    Contains one function, "Func".
    eg. ErrorFunc_MSE.py contains func 'Func(x)' and the derivative of func 'FuncPrime(x)'