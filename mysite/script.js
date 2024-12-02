let treeData = []; // Store the full tree structure for filtering
const treeContainer = document.getElementById('tree-container');

// Function to render the tree
let lastHighlighted = null; // Track the last highlighted node

const renderTree = (nodes, preserveState = false) => {
    const ul = document.createElement('ul');

    nodes.forEach(node => {
        const li = document.createElement('li');
        li.classList.add('tree-node');

        // Add caret for nodes with children
        if (node.children.length > 0) {
            const caret = document.createElement('span');
            caret.classList.add('caret');
            li.appendChild(caret);

            // Preserve expand/collapse state or expand filtered nodes
            if ((preserveState && node.expanded) || node.forceExpand) {
                li.classList.add('expanded');
            }
        }

        const text = document.createElement('span');
        text.textContent = node.text;
        li.appendChild(text);

        if (node.id) {
            // Add click functionality to navigate to content.html
            text.addEventListener('click', (event) => {
                event.stopPropagation(); // Prevent parent node's click handler from firing

                const iframe = window.parent.document.querySelector('#right-side iframe');
                iframe.contentWindow.location.hash = `#${node.id}`;

                // Highlight the clicked node
                if (lastHighlighted) {
                    lastHighlighted.classList.remove('highlighted'); // Remove highlight from previous node
                }
                text.classList.add('highlighted');
                lastHighlighted = text;

                // Ensure leaf node stays expanded (even if it's clicked)
                if (node.children.length === 0) {
                    li.classList.add('expanded'); // Keep leaf expanded
                } else {
                    li.classList.toggle('expanded'); // Toggle for non-leaf nodes
                }

                // Expand parent nodes if clicked node is a leaf
                let parentNode = li.parentElement;
                while (parentNode && parentNode.tagName === 'LI') {
                    parentNode.classList.add('expanded');
                    parentNode = parentNode.parentElement.parentElement;
                }
            });
        }

        // Render children recursively
        if (node.children.length) {
            const childUl = renderTree(node.children, preserveState);
            li.appendChild(childUl);
        }

        ul.appendChild(li);
    });

    return ul;
};




// Filter function
function filterTree() {
    const query = document.getElementById('search-input').value.toLowerCase();

    if (query === '') {
        // Reset to the full tree and preserve user expand/collapse states
        treeContainer.innerHTML = '';
        const treeElement = renderTree(treeData, true); // Pass preserveState = true
        treeContainer.appendChild(treeElement);
        return;
    }

    // Recursively filter nodes
    const filterNodes = (nodes) => {
        return nodes
            .map(node => {
                const children = filterNodes(node.children);
                const matches = node.text.toLowerCase().includes(query);

                if (matches || children.length > 0) {
                    return {
                        ...node,
                        children,
                        forceExpand: matches || children.length > 0, // Mark to expand
                    };
                }

                return null;
            })
            .filter(node => node !== null);
    };

    const filteredTree = filterNodes(treeData);
    treeContainer.innerHTML = ''; // Clear existing tree
    const treeElement = renderTree(filteredTree); // Don't pass preserveState during filtering
    treeContainer.appendChild(treeElement);
}

// Fetch and parse headers from content.html
fetch('headings.html')
    .then(response => response.text())
    .then(data => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, 'text/html');
        const headers = [...doc.querySelectorAll('h1, h2, h3, h4, h5, h6, h7')];

        const buildTree = (headers) => {
            const tree = [];
            const stack = [{ level: 0, children: tree }];

            headers.forEach((header, index) => {
                const level = parseInt(header.tagName.substring(1));
                const node = {
                    text: header.textContent.trim(),
                    id: `header-${level}-${index + 1}`,
                    children: [],
                    expanded: false, // Add expanded state to each node
                };

                while (stack[stack.length - 1].level >= level) {
                    stack.pop();
                }

                stack[stack.length - 1].children.push(node);
                stack.push({ level, children: node.children });
            });

            return tree;
        };

        // Build and render the full tree
        treeData = buildTree(headers);
        const treeElement = renderTree(treeData);
        treeContainer.appendChild(treeElement);
    })
    .catch(error => console.error('Error loading content.html:', error));
