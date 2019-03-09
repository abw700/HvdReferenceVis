var width = 960,
    height = 500

var svg = d3.select(".graph").append("svg")
    .attr("width", width)
    .attr("height", height);

    var g = svg.append("g")
            .attr("class", "everything");

    // Get the JSON data from the input field and parse it.
    var jsonData = document.getElementById('results_json').value;

    graph = JSON.parse(jsonData);

    var simulation = d3.forceSimulation()
        .force("charge", d3.forceManyBody().strength(-200))
        .force("link", d3.forceLink().id(function(d) { return d.pmid; }).distance(40))
        .force("x", d3.forceX(width / 2))
        .force("y", d3.forceY(height / 2))
        .on("tick", ticked);

    var link = g.selectAll(".link"),
        node = g.selectAll(".node");

    // console.log (jsonData);
    // d3.json(jsonData, function(error, graph) {
    // d3.json("../force/force.json", function(error, graph) {
      // if (error) throw error;

      simulation.nodes(graph.nodes);
      simulation.force("link").links(graph.links);

      link = link
        .data(graph.links)
        .enter().append("line")
          .attr("class", "link");

      node = node
        .data(graph.nodes)
        .enter().append("circle")
          .attr("class", "node")
          .attr("r", 6)
          .style("fill", function(d) { return d.id; });


          //add drag capabilities
        var drag_handler = d3.drag()
                .on("start", drag_start)
                .on("drag", drag_drag)
                .on("end", drag_end);

        // Node click capabilities
        node.on("click", function (d) {
            d3.event.stopImmediatePropagation();
            var idObject =  {
              pmid: d.id,
              queryType: 'test'
            };
            // JQUERY AJAX for some info on the nodes
            $.ajax({
              url: '/getIncomingCitations',
              data: idObject,
              type: 'GET',
              success: function(response) {
                var parsed = JSON.parse(response);
                  alert("Number of papers that cite this: " + parsed.numberCiting + "\nPapers that cite this are: \n" + parsed.citingPmids);
              },
              error: function(error) {
                  console.log(error);
              }
            });
        });

        drag_handler(node);

            //add zoom capabilities
        var zoom_handler = d3.zoom()
            .on("zoom", zoom_actions);

        zoom_handler(svg);

      var lables = node.append("text")
        .text(function(d) {
          return d.id;
        })
        .attr('x', 6)
        .attr('y', 3);

      node.append("title")
          .text(function(d) { return d.title  + '\n'+ d.pubyear + '\n' + d.id; });


          //Drag functions
             //d is the node
             function drag_start(d) {
                 if (!d3.event.active) simulation.alphaTarget(0.3).restart();
                 d.fx = d.x;
                 d.fy = d.y;
             }

             //make sure you can't drag the circle outside the box
             function drag_drag(d) {
                 d.fx = d3.event.x;
                 d.fy = d3.event.y;
             }

             function drag_end(d) {
                 if (!d3.event.active) simulation.alphaTarget(0);
                 d.fx = null;
                 d.fy = null;
             }

             //Zoom functions
             function zoom_actions(){
                 g.attr("transform", d3.event.transform)
             }


    // function nodeClicked() {
    //   alert("clicked")
    // }

    function ticked() {
      link.attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      node.attr("cx", function(d) { return d.x; })
          .attr("cy", function(d) { return d.y; });
    }
