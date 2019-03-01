var width = 960,
    height = 500

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

    var simulation = d3.forceSimulation()
        .force("charge", d3.forceManyBody().strength(-200))
        .force("link", d3.forceLink().id(function(d) { return d.pmid; }).distance(40))
        .force("x", d3.forceX(width / 2))
        .force("y", d3.forceY(height / 2))
        .on("tick", ticked);

    var link = svg.selectAll(".link"),
        node = svg.selectAll(".node");

    d3.json("../force/force.json", function(error, graph) {
      if (error) throw error;

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

      var lables = node.append("text")
        .text(function(d) {
          return d.id;
        })
        .attr('x', 6)
        .attr('y', 3);

      node.append("title")
          .text(function(d) { return d.title  + '\n'+ d.pubyear + '\n' + d.id; });
        });

    function generateGraph()
    {
      alert("hi");
    }

    function ticked() {
      link.attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });

      node.attr("cx", function(d) { return d.x; })
          .attr("cy", function(d) { return d.y; });
    }
