document.addEventListener("DOMContentLoaded", function () {
    // Charger les données RDF via une API Flask
    fetch("/export/json")
        .then((response) => response.json())
        .then((data) => {
            // Créer un graphe D3.js à partir des données RDF
            const nodes = new Map();
            const links = [];

            data.forEach((triple) => {
                const subject = triple.subject;
                const predicate = triple.predicate;
                const object = triple.object;

                // Ajouter les nœuds
                if (!nodes.has(subject)) {
                    nodes.set(subject, { id: subject, label: subject.split("/").pop() });
                }
                if (!nodes.has(object)) {
                    nodes.set(object, { id: object, label: object.split("/").pop() });
                }

                // Ajouter les liens
                links.push({ source: subject, target: object, label: predicate.split("/").pop() });
            });

            const width = 800;
            const height = 600;

            const svg = d3.select("#graph")
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            const simulation = d3.forceSimulation(Array.from(nodes.values()))
                .force("link", d3.forceLink(links).id((d) => d.id).distance(150))
                .force("charge", d3.forceManyBody().strength(-400))
                .force("center", d3.forceCenter(width / 2, height / 2));

            // Ajouter les liens
            const link = svg.append("g")
                .selectAll("line")
                .data(links)
                .enter()
                .append("line")
                .attr("stroke", "#aaa")
                .attr("stroke-width", 2);

            // Ajouter les nœuds
            const node = svg.append("g")
                .selectAll("circle")
                .data(Array.from(nodes.values()))
                .enter()
                .append("circle")
                .attr("r", 10)
                .attr("fill", "#007bff");

            // Ajouter les étiquettes
            const label = svg.append("g")
                .selectAll("text")
                .data(Array.from(nodes.values()))
                .enter()
                .append("text")
                .text((d) => d.label)
                .attr("font-size", 12)
                .attr("dx", 15)
                .attr("dy", 4);

            // Mettre à jour les positions des nœuds et des liens
            simulation.on("tick", () => {
                link
                    .attr("x1", (d) => d.source.x)
                    .attr("y1", (d) => d.source.y)
                    .attr("x2", (d) => d.target.x)
                    .attr("y2", (d) => d.target.y);

                node
                    .attr("cx", (d) => d.x)
                    .attr("cy", (d) => d.y);

                label
                    .attr("x", (d) => d.x)
                    .attr("y", (d) => d.y);
            });
        })
        .catch((error) => console.error("Erreur lors du chargement des données :", error));
});