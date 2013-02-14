if (Giraffe.graph)
{
    $.getScript(Giraffe.staticUrl+'static/giraffe/js/highcharts.js', function(){
        $.getScript(Giraffe.staticUrl+'static/giraffe/js/exporting.js', function(){
            $(function () {
                var chart;
                $(document).ready(function() {
                    chart = new Highcharts.Chart({
                        chart: {
                            renderTo: Giraffe.graph.target,
                            type: Giraffe.graph.type,
                            marginRight: 130,
                            marginBottom: 25
                        },
                        title: {
                            text: Giraffe.graph.title,
                            x: -20 //center
                        },
                        subtitle: {
                            text: Giraffe.graph.subtitle,
                            x: -20
                        },
                        xAxis: {
                            categories: Giraffe.graph.x.data
                        },
                        yAxis: {
                            title: {
                                text: Giraffe.graph.y.label
                            },
                            plotLines: [{
                                value: 0,
                                width: 1,
                                color: '#808080'
                            }]
                        },
                        tooltip: {
                            formatter: function() {
                                    return '<b>'+ this.series.name +'</b><br/>'+
                                    this.x +': '+ this.y +'';
                            }
                        },
                        legend: {
                            layout: 'vertical',
                            align: 'right',
                            verticalAlign: 'top',
                            x: -10,
                            y: 100,
                            borderWidth: 0
                        },
                        series: Giraffe.graph.y.series
                    });
                });
                
            });
        })
    })
}