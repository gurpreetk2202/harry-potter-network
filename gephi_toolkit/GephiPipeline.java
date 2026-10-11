/*
 * GephiPipeline.java
 * ------------------
 * Reproduces, step by step, the workflow described in report/gephi_instructions.md
 * using the official Gephi Toolkit (the same Java engine that runs inside Gephi Desktop).
 *
 *   1. Import data/nodes.csv (nodes table) and data/edges.csv (edges table, appended)
 *   2. Statistics: Average Degree, Avg. Weighted Degree, Network Diameter (betweenness),
 *      Modularity (Louvain, weighted, resolution 1.0)
 *   3. Layout: ForceAtlas2, then ForceAtlas2 with "Prevent Overlap"
 *   4. Appearance: node size = Degree (ranking), node colour = Modularity Class (partition)
 *   5. Preview: labels on, edge thickness = Weight
 *   6. Export: visualization/gephi_project.gephi, PNG and PDF, plus Gephi's node table
 *
 * Build & run: see gephi_toolkit/run.sh
 */

import java.awt.Color;
import java.awt.Font;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

import org.gephi.appearance.api.AppearanceController;
import org.gephi.appearance.api.AppearanceModel;
import org.gephi.appearance.api.Function;
import org.gephi.appearance.api.Partition;
import org.gephi.appearance.api.PartitionFunction;
import org.gephi.appearance.plugin.PartitionElementColorTransformer;
import org.gephi.appearance.plugin.RankingNodeSizeTransformer;
import org.gephi.graph.api.Column;
import org.gephi.graph.api.GraphController;
import org.gephi.graph.api.GraphModel;
import org.gephi.graph.api.Node;
import org.gephi.graph.api.UndirectedGraph;
import org.gephi.io.exporter.api.ExportController;
import org.gephi.io.exporter.preview.PDFExporter;
import org.gephi.io.exporter.preview.PNGExporter;
import org.gephi.io.importer.api.Container;
import org.gephi.io.importer.api.EdgeDirectionDefault;
import org.gephi.io.importer.api.ImportController;
import org.gephi.io.importer.plugin.file.spreadsheet.ImporterSpreadsheetCSV;
import org.gephi.io.importer.plugin.file.spreadsheet.process.SpreadsheetGeneralConfiguration.Mode;
import org.gephi.io.processor.plugin.AppendProcessor;
import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2;
import org.gephi.layout.plugin.forceAtlas2.ForceAtlas2Builder;
import org.gephi.layout.plugin.labelAdjust.LabelAdjust;
import org.gephi.layout.plugin.labelAdjust.LabelAdjustBuilder;
import org.gephi.preview.api.PreviewController;
import org.gephi.preview.api.PreviewModel;
import org.gephi.preview.api.PreviewProperty;
import org.gephi.preview.types.DependantColor;
import org.gephi.preview.types.DependantOriginalColor;
import org.gephi.preview.types.EdgeColor;
import org.gephi.project.api.ProjectController;
import org.gephi.project.io.SaveTask;
import org.gephi.project.api.Workspace;
import org.gephi.statistics.plugin.Degree;
import org.gephi.statistics.plugin.GraphDistance;
import org.gephi.statistics.plugin.Modularity;
import org.gephi.statistics.plugin.WeightedDegree;
import org.openide.util.Lookup;

public class GephiPipeline {

    public static void main(String[] args) throws Exception {
        File root = new File(args.length > 0 ? args[0] : "..").getCanonicalFile();
        File vis = new File(root, "visualization");
        vis.mkdirs();

        // ---------- 1. New project + import ----------
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace ws = pc.getCurrentWorkspace();
        ImportController ic = Lookup.getDefault().lookup(ImportController.class);

        ImporterSpreadsheetCSV nodeImporter = new ImporterSpreadsheetCSV();
        nodeImporter.setFile(new File(root, "data/nodes.csv"));
        nodeImporter.setMode(Mode.NODES_TABLE);
        nodeImporter.setColumnClass("Id", String.class);
        nodeImporter.setColumnClass("Label", String.class);
        nodeImporter.setColumnClass("house", String.class);
        nodeImporter.setColumnClass("gender", String.class);
        nodeImporter.setColumnClass("schoolyear", Integer.class);
        nodeImporter.setColumnClass("books_with_ties", Integer.class);
        Container nodes = ic.importFile(new File(root, "data/nodes.csv"), nodeImporter);
        nodes.getLoader().setEdgeDefault(EdgeDirectionDefault.UNDIRECTED);
        ic.process(nodes, new DefaultProcessor(), ws);

        ImporterSpreadsheetCSV edgeImporter = new ImporterSpreadsheetCSV();
        edgeImporter.setFile(new File(root, "data/edges.csv"));
        edgeImporter.setMode(Mode.EDGES_TABLE);
        edgeImporter.setColumnClass("Source", String.class);
        edgeImporter.setColumnClass("Target", String.class);
        edgeImporter.setColumnClass("Type", String.class);
        edgeImporter.setColumnClass("Weight", Double.class);
        edgeImporter.setColumnClass("books", String.class);
        edgeImporter.setColumnClass("directed_ties", Integer.class);
        Container edges = ic.importFile(new File(root, "data/edges.csv"), edgeImporter);
        edges.getLoader().setEdgeDefault(EdgeDirectionDefault.UNDIRECTED);
        edges.getLoader().setAllowAutoNode(false); // an edge to an unknown node is an error, not a new node
        ic.process(edges, new AppendProcessor(), ws);

        GraphModel gm = Lookup.getDefault().lookup(GraphController.class).getGraphModel(ws);
        UndirectedGraph g = gm.getUndirectedGraph();
        System.out.printf("Imported: %d nodes, %d edges, directed=%s%n",
                g.getNodeCount(), g.getEdgeCount(), gm.isDirected());

        // ---------- 2. Statistics ----------
        Degree degree = new Degree();
        degree.execute(gm);
        WeightedDegree wdegree = new WeightedDegree();
        wdegree.execute(gm);
        GraphDistance distance = new GraphDistance();
        distance.setDirected(false);
        distance.setNormalized(false);
        distance.execute(gm);
        Modularity modularity = new Modularity();
        modularity.setRandom(false);      // deterministic run (Desktop default is "Randomize" on)
        modularity.setUseWeight(true);
        modularity.setResolution(1.0);
        modularity.execute(gm);
        System.out.printf("Average degree: %.3f%n", degree.getAverageDegree());
        System.out.printf("Diameter: %.0f, average path length: %.3f%n", distance.getDiameter(), distance.getPathLength());
        System.out.printf("Modularity Q: %.3f%n", modularity.getModularity());

        // ---------- 3. Layout: ForceAtlas2 ----------
        // (labels are drawn in Preview using the label column; Label Adjust needs them on nodes)
        Random rnd = new Random(42);           // fixed start positions -> reproducible picture
        for (Node n : g.getNodes()) {
            n.setX((float) (rnd.nextDouble() * 1000 - 500));
            n.setY((float) (rnd.nextDouble() * 1000 - 500));
        }
        ForceAtlas2 fa2 = new ForceAtlas2Builder().buildLayout();
        fa2.setGraphModel(gm);
        fa2.resetPropertiesValues();
        fa2.setThreadsCount(1);
        fa2.setScalingRatio(60.0);         // more repulsion -> more space between nodes
        fa2.setStrongGravityMode(true);    // keeps the separate Slytherin component close by
        fa2.setGravity(1.0);
        fa2.setEdgeWeightInfluence(1.0);
        fa2.setLinLogMode(false);
        fa2.setBarnesHutOptimize(false);
        fa2.setAdjustSizes(false);
        fa2.initAlgo();
        for (int i = 0; i < 3000 && fa2.canAlgo(); i++) fa2.goAlgo();
        fa2.endAlgo();

        // ---------- 4. Appearance (size must be set before Prevent Overlap) ----------
        AppearanceController ac = Lookup.getDefault().lookup(AppearanceController.class);
        AppearanceModel am = ac.getModel(ws);

        Column degreeCol = gm.getNodeTable().getColumn(Degree.DEGREE);
        Function sizeByDegree = am.getNodeFunction(degreeCol, RankingNodeSizeTransformer.class);
        RankingNodeSizeTransformer sizeT = sizeByDegree.getTransformer();
        sizeT.setMinSize(6f);
        sizeT.setMaxSize(32f);
        ac.transform(sizeByDegree);

        Column modCol = gm.getNodeTable().getColumn(Modularity.MODULARITY_CLASS);
        Function colorByCommunity = am.getNodeFunction(modCol, PartitionElementColorTransformer.class);
        Partition partition = ((PartitionFunction) colorByCommunity).getPartition();
        // Professional colour-blind-friendly palette (Okabe-Ito), biggest community first
        Color[] palette = {
            new Color(0x0072B2), new Color(0xD55E00), new Color(0x009E73), new Color(0xCC79A7),
            new Color(0xE69F00), new Color(0x56B4E9), new Color(0x999999), new Color(0xF0E442)};
        List<Object> classes = new ArrayList<>(partition.getSortedValues(g)); // sorted by size, desc
        for (int i = 0; i < classes.size(); i++) partition.setColor(classes.get(i), palette[i % palette.length]);
        ac.transform(colorByCommunity);

        // second ForceAtlas2 pass with Prevent Overlap now that nodes have their final size
        fa2.setAdjustSizes(true);
        fa2.initAlgo();
        for (int i = 0; i < 1000 && fa2.canAlgo(); i++) fa2.goAlgo();
        fa2.endAlgo();

        // Label Adjust: nudges nodes apart so that labels do not overlap
        LabelAdjust labelAdjust = new LabelAdjustBuilder().buildLayout();
        labelAdjust.setGraphModel(gm);
        labelAdjust.resetPropertiesValues();
        labelAdjust.initAlgo();
        for (int i = 0; i < 2000 && labelAdjust.canAlgo(); i++) labelAdjust.goAlgo();
        labelAdjust.endAlgo();

        // ---------- 5. Preview settings ----------
        PreviewController prc = Lookup.getDefault().lookup(PreviewController.class);
        PreviewModel pm = prc.getModel(ws);
        pm.getProperties().putValue(PreviewProperty.BACKGROUND_COLOR, Color.WHITE);
        pm.getProperties().putValue(PreviewProperty.SHOW_NODE_LABELS, Boolean.TRUE);
        pm.getProperties().putValue(PreviewProperty.NODE_LABEL_FONT, new Font("SansSerif", Font.BOLD, 6));
        pm.getProperties().putValue(PreviewProperty.NODE_LABEL_PROPORTIONAL_SIZE, Boolean.FALSE);
        pm.getProperties().putValue(PreviewProperty.NODE_LABEL_COLOR, new DependantOriginalColor(new Color(0x222222)));
        pm.getProperties().putValue(PreviewProperty.NODE_LABEL_OUTLINE_SIZE, 2.5f);
        pm.getProperties().putValue(PreviewProperty.NODE_LABEL_OUTLINE_COLOR, new DependantColor(Color.WHITE));
        pm.getProperties().putValue(PreviewProperty.NODE_LABEL_OUTLINE_OPACITY, 85f);
        pm.getProperties().putValue(PreviewProperty.NODE_BORDER_WIDTH, 1.2f);
        pm.getProperties().putValue(PreviewProperty.NODE_BORDER_COLOR, new DependantColor(Color.WHITE));
        pm.getProperties().putValue(PreviewProperty.EDGE_CURVED, Boolean.FALSE);
        pm.getProperties().putValue(PreviewProperty.EDGE_COLOR, new EdgeColor(new Color(0x8A8A8A)));
        pm.getProperties().putValue(PreviewProperty.EDGE_OPACITY, 55f);
        pm.getProperties().putValue(PreviewProperty.EDGE_RESCALE_WEIGHT, Boolean.TRUE);
        pm.getProperties().putValue(PreviewProperty.EDGE_RESCALE_WEIGHT_MIN, 0.4f);
        pm.getProperties().putValue(PreviewProperty.EDGE_RESCALE_WEIGHT_MAX, 4.0f);
        prc.refreshPreview(ws);

        // ---------- 6. Export ----------
        ExportController ec = Lookup.getDefault().lookup(ExportController.class);
        PNGExporter png = (PNGExporter) ec.getExporter("png");
        png.setWorkspace(ws);
        png.setWidth(4000);
        png.setHeight(3200);
        png.setMargin(4);
        png.setTransparentBackground(false);
        ec.exportFile(new File(vis, "harry_potter_network_gephi_raw.png"), png);

        PDFExporter pdf = (PDFExporter) ec.getExporter("pdf");
        pdf.setWorkspace(ws);
        ec.exportFile(new File(vis, "harry_potter_network.pdf"), pdf);

        // node table as computed by Gephi (Data Laboratory -> Export table)
        try (PrintWriter out = new PrintWriter(new FileWriter(new File(root, "analysis/gephi_node_metrics.csv")))) {
            out.println("Id,Label,degree,weighted_degree,betweenness,modularity_class,color_hex,x,y");
            for (Node n : g.getNodes()) {
                Color c = n.getColor();
                out.printf("%s,%s,%s,%s,%.3f,%s,#%02X%02X%02X,%.1f,%.1f%n",
                        n.getId(), n.getLabel(), n.getAttribute(Degree.DEGREE),
                        n.getAttribute(WeightedDegree.WDEGREE), (Double) n.getAttribute(GraphDistance.BETWEENNESS),
                        n.getAttribute(Modularity.MODULARITY_CLASS),
                        c.getRed(), c.getGreen(), c.getBlue(), n.x(), n.y());
            }
        }
        // legend information for the community colours
        try (PrintWriter out = new PrintWriter(new FileWriter(new File(root, "analysis/gephi_communities.csv")))) {
            out.println("modularity_class,color_hex,size,share_percent");
            for (Object v : classes) {
                Color c = partition.getColor(v);
                out.printf("%s,#%02X%02X%02X,%d,%.2f%n", v, c.getRed(), c.getGreen(), c.getBlue(),
                        partition.count(v, g), partition.percentage(v, g));
            }
        }
        try (PrintWriter out = new PrintWriter(new FileWriter(new File(root, "analysis/gephi_statistics_summary.txt")))) {
            out.printf("Nodes: %d%nEdges: %d%nGraph type: %s%n", g.getNodeCount(), g.getEdgeCount(),
                    gm.isDirected() ? "directed" : "undirected");
            out.printf("Average degree: %.3f%n", degree.getAverageDegree());
            out.printf("Average weighted degree: %.3f%n", wdegree.getAverageDegree());
            out.printf("Network diameter: %.0f%n", distance.getDiameter());
            out.printf("Average path length: %.3f%n", distance.getPathLength());
            out.printf("Modularity (Louvain, weighted, resolution 1.0, randomize off): %.3f%n", modularity.getModularity());
            out.printf("Number of communities: %d%n", classes.size());
        }

        // ProjectController.saveProject() runs in a background thread; run the same SaveTask
        // synchronously so the file is fully written before the program exits.
        // Toolkit 0.10.1 quirk: if the target does not exist yet, SaveTask's clean-up step deletes
        // the file it just wrote. With an existing target it writes a temp file and renames it over.
        File gephiFile = new File(vis, "gephi_project.gephi");
        gephiFile.createNewFile();
        boolean saved = new SaveTask(pc.getCurrentProject(), gephiFile).run();
        if (!saved || gephiFile.length() == 0)
            throw new IllegalStateException("Saving the .gephi project failed");
        System.out.println("Done: visualization/gephi_project.gephi, PNG, PDF and analysis/gephi_*.csv");
    }
}
