var Giraffe = function(Giraffe){
    var defaults = {
        graph: null,
        staticUrl: '/'
    };
    if (typeof(Giraffe) == 'undefined')
    {
        return defaults;
    }
    else
    {
        for (key in defaults)
        {
            if (typeof(Giraffe[key]) == 'undefined')
                Giraffe[key] = defaults[key];
        }
        return Giraffe;
    }
}(Giraffe);