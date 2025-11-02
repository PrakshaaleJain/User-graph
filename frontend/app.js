const API_URL = window.location.origin;

let cy;
let graphData = { nodes: [], edges: [] };
let users = [];
let transactions = [];

// Relationship type colors
const edgeColors = {
    'SENT': '#10b981',
    'RECEIVED_BY': '#10b981',
    // 'SHARED_EMAIL': '#ef4444',
    // 'SHARED_PHONE': '#8b5cf6',
    // 'SHARED_ADDRESS': '#ec4899',
    // 'SHARED_PAYMENT_METHOD': '#3b82f6',
    // 'CREDIT_TO': '#14b8a6',
    // 'DEBIT_FROM': '#14b8a6',
    // 'SHARED_DEVICE': '#f97316',
    // 'SHARED_IP': '#f97316'
};

// Initialize Cytoscape
function initCytoscape() {
    cy = cytoscape({
        container: document.getElementById('cy'),
        
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-size': '12px',
                    'color': '#fff',
                    'text-outline-width': 2,
                    'text-outline-color': 'data(color)',
                    'background-color': 'data(color)',
                    'width': 'data(size)',
                    'height': 'data(size)',
                    'overlay-padding': '6px',
                    'border-width': 2,
                    'border-color': '#fff'
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-width': 3,
                    'border-color': '#fbbf24',
                    'overlay-opacity': 0.2,
                    'overlay-color': '#fbbf24'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': 'data(color)',
                    'target-arrow-color': 'data(color)',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'opacity': 0.7,
                    'label': 'data(type)',
                    'font-size': '10px',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -10,
                    'color': '#666'
                }
            },
            {
                selector: 'edge:selected',
                style: {
                    'width': 4,
                    'opacity': 1
                }
            },
            {
                selector: '.highlighted',
                style: {
                    'border-width': 4,
                    'border-color': '#fbbf24'
                }
            },
            {
                selector: '.faded',
                style: {
                    'opacity': 0.2
                }
            }
        ],
        
        layout: {
            name: 'cose',
            animate: true,
            animationDuration: 500,
            idealEdgeLength: 100,
            nodeOverlap: 20,
            refresh: 20,
            fit: true,
            padding: 30,
            randomize: false,
            componentSpacing: 100,
            nodeRepulsion: 400000,
            edgeElasticity: 100,
            nestingFactor: 5,
            gravity: 80,
            numIter: 1000,
            initialTemp: 200,
            coolingFactor: 0.95,
            minTemp: 1.0
        }
    });

    // Node click event
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        const nodeData = node.data();
        
        // Highlight connected nodes
        const connectedNodes = node.neighborhood().nodes();
        const connectedEdges = node.connectedEdges();
        
        cy.elements().removeClass('highlighted').addClass('faded');
        node.removeClass('faded').addClass('highlighted');
        connectedNodes.removeClass('faded').addClass('highlighted');
        connectedEdges.removeClass('faded');
        
        // Show details
        if (nodeData.type === 'user') {
            showUserDetails(nodeData);
        } else {
            showTransactionDetails(nodeData);
        }
    });

    // Edge click event
    cy.on('tap', 'edge', function(evt) {
        const edge = evt.target;
        const edgeData = edge.data();
        
        console.log('Relationship:', edgeData.type);
        console.log('From:', edgeData.source, 'To:', edgeData.target);
    });

    // Background click - reset
    cy.on('tap', function(evt) {
        if (evt.target === cy) {
            cy.elements().removeClass('highlighted faded');
        }
    });
}

// Load graph data
async function loadGraph() {
    document.getElementById('loading').style.display = 'block';
    
    try {
        // Fetch graph data
        const response = await fetch(`${API_URL}/graph`);
        graphData = await response.json();
        
        // Fetch users and transactions for sidebar
        const usersResponse = await fetch(`${API_URL}/users`);
        users = await usersResponse.json();
        
        const txnsResponse = await fetch(`${API_URL}/transactions`);
        transactions = await txnsResponse.json();
        
        // Process and display
        processGraphData();
        renderLists();
        updateStats();
        
        document.getElementById('loading').style.display = 'none';
    } catch (error) {
        console.error('Error loading graph:', error);
        document.getElementById('loading').textContent = 'Error loading data. Check console.';
    }
}

// Process graph data for Cytoscape
function processGraphData() {
    const elements = [];
    
    // Add nodes
    graphData.nodes.forEach(node => {
        const nodeData = node.data;
        elements.push({
            group: 'nodes',
            data: {
                id: nodeData.id,
                label: nodeData.label,
                type: nodeData.type,
                color: nodeData.type === 'user' ? '#667eea' : '#f59e0b',
                size: nodeData.type === 'user' ? 50 : 40,
                ...nodeData
            }
        });
    });
    
    // Add edges
    graphData.edges.forEach(edge => {
        const edgeData = edge.data;
        elements.push({
            group: 'edges',
            data: {
                id: edgeData.id,
                source: edgeData.source,
                target: edgeData.target,
                type: edgeData.type,
                color: edgeColors[edgeData.type] || '#94a3b8'
            }
        });
    });
    
    // Update graph
    cy.elements().remove();
    cy.add(elements);
    cy.layout({
        name: 'cose',
        animate: true,
        animationDuration: 500,
        idealEdgeLength: 100,
        nodeOverlap: 20,
        refresh: 20,
        fit: true,
        padding: 30
    }).run();
}

// Render sidebar lists
function renderLists() {
    const usersList = document.getElementById('usersList');
    const transactionsList = document.getElementById('transactionsList');
    
    // Render users
    usersList.innerHTML = users.map(user => `
        <div class="item" onclick="selectNode('${user.user_id}')">
            <div class="item-id">${user.user_id}</div>
            <div class="item-details">
                ${user.name || 'N/A'}<br>
                ${user.email || 'N/A'}
            </div>
        </div>
    `).join('');
    
    // Render transactions
    transactionsList.innerHTML = transactions.map(txn => `
        <div class="item" onclick="selectNode('${txn.txn_id}')">
            <div class="item-id">${txn.txn_id}</div>
            <div class="item-details">
                Amount: $${txn.amount || 0}<br>
                Device: ${txn.device_id || 'N/A'}
            </div>
        </div>
    `).join('');
}

// Select and highlight node
function selectNode(nodeId) {
    const node = cy.getElementById(nodeId);
    if (node.length > 0) {
        cy.elements().removeClass('highlighted faded');
        
        const connectedNodes = node.neighborhood().nodes();
        const connectedEdges = node.connectedEdges();
        
        cy.elements().addClass('faded');
        node.removeClass('faded').addClass('highlighted');
        connectedNodes.removeClass('faded').addClass('highlighted');
        connectedEdges.removeClass('faded');
        
        cy.animate({
            center: { eles: node },
            zoom: 1.5
        }, {
            duration: 500
        });
        
        // Update sidebar selection
        document.querySelectorAll('.item').forEach(item => item.classList.remove('selected'));
        event.target.closest('.item').classList.add('selected');
    }
}

// Show user details
async function showUserDetails(userData) {
    try {
        const response = await fetch(`${API_URL}/relationships/user/${userData.id}`);
        const relationships = await response.json();
        console.log('User Relationships:', relationships);
    } catch (error) {
        console.error('Error fetching user relationships:', error);
    }
}

// Show transaction details
async function showTransactionDetails(txnData) {
    try {
        const response = await fetch(`${API_URL}/relationships/transaction/${txnData.id}`);
        const relationships = await response.json();
        console.log('Transaction Relationships:', relationships);
    } catch (error) {
        console.error('Error fetching transaction relationships:', error);
    }
}

// Update stats
function updateStats() {
    document.getElementById('userCount').textContent = users.length;
    document.getElementById('txnCount').textContent = transactions.length;
    document.getElementById('relCount').textContent = graphData.edges.length;
}

// Search functionality
document.getElementById('searchBox').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    
    if (searchTerm === '') {
        cy.elements().removeClass('highlighted faded');
        return;
    }
    
    cy.elements().addClass('faded');
    
    const matchedNodes = cy.nodes().filter(node => {
        const data = node.data();
        return data.label.toLowerCase().includes(searchTerm) ||
               data.id.toLowerCase().includes(searchTerm) ||
               (data.name && data.name.toLowerCase().includes(searchTerm)) ||
               (data.email && data.email.toLowerCase().includes(searchTerm));
    });
    
    matchedNodes.removeClass('faded').addClass('highlighted');
    matchedNodes.neighborhood().removeClass('faded');
});

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    initCytoscape();
    loadGraph();
});
