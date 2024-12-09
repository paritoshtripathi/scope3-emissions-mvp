CREATE CONSTRAINT unique_node_id ON (n:Node) ASSERT n.id IS UNIQUE;
