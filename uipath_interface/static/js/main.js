let actions = {};
let bboxFiles = [];
let selectedNode = null;
let isPlaying = false;
let currentScope = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    // Add the stop button if it doesn't exist
    createStopButtonIfNeeded();
    
    // Create toast container for notifications
    createToastContainer();
    
    // Ensure the action items are draggable
    setupActionItemsDraggable();
    
    // Setup visual feedback for drag and drop
    setupDragAndDropVisualFeedback();
    
    // Fetch available actions and bbox files
    try {
        const [actionsResponse, bboxFilesResponse, scriptsResponse] = await Promise.all([
            fetch('/api/actions'),
            fetch('/api/bbox_files'),
            fetch('/api/scripts')
        ]);
        
        actions = await actionsResponse.json();
        bboxFiles = await bboxFilesResponse.json();
        const scripts = await scriptsResponse.json();
        
        // Populate scripts dropdown
        const scriptSelect = document.getElementById('scriptSelect');
        scripts.forEach(script => {
            const option = document.createElement('option');
            option.value = script;
            option.textContent = script;
            scriptSelect.appendChild(option);
        });
        
        // Add event listener for script selection
        scriptSelect.addEventListener('change', async (e) => {
            const selectedScript = e.target.value;
            if (selectedScript) {
                try {
                    const response = await fetch(`/api/load_script?name=${encodeURIComponent(selectedScript)}`);
                    const data = await response.json();
                    console.log('Loaded script data:', data);
                    
                    if (data.actions) {
                        // Clear existing actions
                        const canvas = document.getElementById('canvas');
                        canvas.innerHTML = '';
                        
                        // Add new actions
                        data.actions.forEach(action => {
                            console.log('Processing action:', action);
                            
                            if (action.id === 'screen_scope') {
                                const node = createScreenScopeNode(action.properties);
                                canvas.appendChild(node);
                                
                                // Add actions within the screen scope
                                if (action.properties.actions) {
                                    const scopeContent = node.querySelector('.scope-actions-container');
                                    action.properties.actions.forEach(scopeAction => {
                                        console.log('Processing scope action:', scopeAction);
                                        const actionNode = createActionNode(scopeAction.id, actions[scopeAction.id]);
                                        if (scopeAction.properties) {
                                            console.log('Scope action properties:', scopeAction.properties);
                                            actionNode.dataset.properties = JSON.stringify(scopeAction.properties);
                                            updateNodeDisplay(actionNode);
                                        }
                                        scopeContent.appendChild(actionNode);
                                    });
                                }
                            } else {
                                const node = createActionNode(action.id, actions[action.id]);
                                if (action.properties) {
                                    console.log('Action properties:', action.properties);
                                    node.dataset.properties = JSON.stringify(action.properties);
                                    updateNodeDisplay(node);
                                }
                                canvas.appendChild(node);
                            }
                        });
                        
                        updateAllOrderNumbers();
                        // Update placeholder visibility after loading script
                        updatePlaceholderVisibility();
                    }
                } catch (error) {
                    console.error('Error loading script:', error);
                }
            }
        });
        
        initializeDragAndDrop();
        initializeSaveButton();
        initializePlayButton();
        // Initial update of placeholder visibility
        updatePlaceholderVisibility();
    } catch (error) {
        console.error('Error initializing application:', error);
    }
});

// Add a dedicated function to ensure action items are draggable
function setupActionItemsDraggable() {
    const actionsList = document.getElementById('actionsList');
    if (!actionsList) {
        console.error('Could not find actionsList element');
        return;
    }
    
    // Get all action items
    const actionItems = actionsList.querySelectorAll('.action-item');
    console.log(`Found ${actionItems.length} action items in setupActionItemsDraggable`);
    
    // Apply draggable property and event handlers directly
    actionItems.forEach(item => {
        // Ensure the item is draggable
        item.draggable = true;
        
        // Remove existing handlers to avoid duplicates
        item.removeEventListener('dragstart', handleActionItemDragStart);
        item.removeEventListener('dragend', handleActionItemDragEnd);
        
        // Add new handlers
        item.addEventListener('dragstart', handleActionItemDragStart);
        item.addEventListener('dragend', handleActionItemDragEnd);
    });
}

// Separate handlers for action item dragging from sidebar
function handleActionItemDragStart(e) {
    console.log(`Action item drag start: ${e.target.dataset.actionId}`);
    
    // Mark as sidebar item
    e.target.classList.add('dragging-from-sidebar');
    e.target.classList.add('dragging');
    
    // Set the data transfer
    const actionId = e.target.dataset.actionId;
    e.dataTransfer.setData('text/plain', actionId);
    
    // Check if this is a screen scope and set appropriate data
    if (actionId === 'screen_scope') {
        e.dataTransfer.setData('application/json', JSON.stringify({
            type: 'screen_scope',
            name: 'New Screen Scope',
            csvPath: '',
            fromSidebar: true
        }));
    } else {
        e.dataTransfer.setData('application/json', JSON.stringify({
            type: 'action',
            actionId: actionId,
            properties: '{}',
            fromSidebar: true
        }));
    }
    
    // Set the drag effect
    e.dataTransfer.effectAllowed = 'copy';
}

function handleActionItemDragEnd(e) {
    console.log('Action item drag end');
    e.target.classList.remove('dragging-from-sidebar');
    e.target.classList.remove('dragging');
}

// Create the stop button if it doesn't exist in the HTML
function createStopButtonIfNeeded() {
    if (!document.getElementById('stopScript')) {
        const playBtn = document.getElementById('playScript');
        if (playBtn) {
            const stopBtn = document.createElement('button');
            stopBtn.id = 'stopScript';
            stopBtn.className = 'btn btn-danger ms-2';
            stopBtn.innerHTML = '<i class="fas fa-stop"></i> Stop';
            stopBtn.title = 'Stop the currently running script';
            
            // Insert the stop button after the play button
            playBtn.insertAdjacentElement('afterend', stopBtn);
        }
    }
}

function initializeDragAndDrop() {
    console.log("Initializing drag and drop");
    const actionItems = document.querySelectorAll('.action-item');
    const canvas = document.getElementById('canvas');
    
    // Add a welcome placeholder if canvas is empty
    if (canvas.children.length === 0) {
        const welcomePlaceholder = document.createElement('div');
        welcomePlaceholder.className = 'welcome-placeholder';
        welcomePlaceholder.innerHTML = `
            <div class="text-center p-5 text-muted">
                <h4>Welcome to the Script Builder</h4>
                <p>Drag items from the sidebar to build your script</p>
                <div class="row mt-3">
                    <div class="col">
                        <div class="card mb-2">
                            <div class="card-body">
                                <h5><i class="fas fa-desktop"></i> Screen Scopes</h5>
                                <p>Drag a screen scope to organize actions</p>
                            </div>
                        </div>
                    </div>
                    <div class="col">
                        <div class="card">
                            <div class="card-body">
                                <h5><i class="fas fa-mouse-pointer"></i> Actions</h5>
                                <p>Drag actions to build your workflow</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        canvas.appendChild(welcomePlaceholder);
        
        // Remove the welcome placeholder when dragging over the canvas
        canvas.addEventListener('dragover', () => {
            const placeholder = canvas.querySelector('.welcome-placeholder');
            if (placeholder) {
                placeholder.style.display = 'none';
            }
        });
        
        // If dropping is canceled, show the placeholder again if canvas is empty
        canvas.addEventListener('dragleave', (e) => {
            if (!e.currentTarget.contains(e.relatedTarget)) {
                const placeholder = canvas.querySelector('.welcome-placeholder');
                if (placeholder && canvas.children.length <= 1) {
                    placeholder.style.display = '';
                }
            }
        });
    }
    
    // Set up drag start for action items in the sidebar
    console.log(`Found ${actionItems.length} action items to make draggable`);
    
    // Set draggable attribute on all action items
    actionItems.forEach(item => {
        // Ensure the item is draggable
        item.setAttribute('draggable', 'true');
        
        item.addEventListener('dragstart', (e) => {
            console.log(`Drag started for action: ${e.target.dataset.actionId}`);
            // Mark this as a sidebar item being dragged
            item.classList.add('dragging-from-sidebar');
            e.dataTransfer.setData('text/plain', e.target.dataset.actionId);
            e.dataTransfer.setData('application/json', JSON.stringify({
                type: 'action',
                actionId: e.target.dataset.actionId,
                properties: '{}',
                fromSidebar: true
            }));
            e.target.classList.add('dragging');
            
            // Set a drag image or effect
            e.dataTransfer.effectAllowed = 'copy';
        });
        
        item.addEventListener('dragend', (e) => {
            console.log('Drag ended for action item');
            item.classList.remove('dragging-from-sidebar');
            e.target.classList.remove('dragging');
        });
    });
    
    // Check if the canvas is properly handling dragover
    canvas.addEventListener('dragover', (e) => {
        e.preventDefault();
        console.log('Canvas dragover event fired');
        e.dataTransfer.dropEffect = 'copy';
    });
    
    // Set up drop handling for the main canvas
    canvas.addEventListener('drop', (e) => {
        e.preventDefault();
        console.log('Drop event occurred on canvas');
        
        // Remove welcome placeholder if it exists
        const welcomePlaceholder = canvas.querySelector('.welcome-placeholder');
        if (welcomePlaceholder) {
            welcomePlaceholder.remove();
        }
        
        // If we're already moving an existing draggable node, don't create a new one
        const draggingNode = document.querySelector('.dragging');
        
        // Get the data from the drag operation
        const data = e.dataTransfer.getData('text/plain');
        const dragDataStr = e.dataTransfer.getData('application/json');
        
        console.log('Drop data text/plain:', data);
        console.log('Drop data application/json:', dragDataStr);
        
        // Check if we're dropping from the sidebar
        const isFromSidebar = document.querySelector('.dragging-from-sidebar');
        console.log('Is drop from sidebar:', !!isFromSidebar);
        
        // If we have a dragging node that's not from the sidebar, just update order
        if (draggingNode && !isFromSidebar) {
            console.log('Moving existing node');
            updateAllOrderNumbers();
            return;
        }
        
        // Try to parse the JSON data
        let dragData = null;
        try {
            if (dragDataStr) {
                dragData = JSON.parse(dragDataStr);
                console.log('Parsed drag data:', dragData);
            }
        } catch (error) {
            console.error('Error parsing drag data:', error);
        }
        
        // Handle drop based on what was dragged
        if (dragData && dragData.type === 'screen_scope') {
            // Handle screen scope drop
            console.log('Creating new screen scope');
            const placeholder = document.querySelector('.canvas-placeholder');
            if (placeholder) {
                placeholder.remove();
            }
            
            const node = createScreenScopeNode({
                name: dragData.name || 'New Screen Scope',
                csv_path: dragData.csvPath || ''
            });
            
            // Find the right position to insert
            const afterElement = getDragAfterElement(canvas, e.clientY);
            if (afterElement) {
                canvas.insertBefore(node, afterElement);
            } else {
                canvas.appendChild(node);
            }
            
            // Force the scope container to be fully visible
            const scopeContent = node.querySelector('.scope-content');
            const scopePreview = node.querySelector('.scope-preview');
            if (scopeContent) scopeContent.style.display = 'block';
            if (scopePreview) scopePreview.style.display = 'block';
            
            // Ensure placeholder visibility is updated
            updatePlaceholderVisibility();
        } 
        else if ((dragData && dragData.type === 'action') || data) {
            // Handle action drop - either from JSON data or plain text fallback
            const actionId = dragData ? dragData.actionId : data;
            console.log('Creating new action node with ID:', actionId);
            
            const action = actions[actionId];
            if (!action) {
                console.error('Action not found:', actionId);
                return;
            }
            
            const placeholder = document.querySelector('.canvas-placeholder');
            if (placeholder) {
                placeholder.remove();
            }
            
            // Check if we're dropping into a screen scope
            const scopeContent = e.target.closest('.scope-actions-container');
            if (scopeContent) {
                console.log('Dropping into screen scope');
                // Create a new action node
                const actionNode = createActionNode(actionId, action);
                
                // Add any properties from the drag data
                if (dragData && dragData.properties && dragData.properties !== '{}') {
                    actionNode.dataset.properties = dragData.properties;
                    updateNodeDisplay(actionNode);
                }
                
                // Add to scope container
                scopeContent.appendChild(actionNode);
            } else {
                console.log('Dropping directly on canvas');
                // Create a new action node
                const node = createActionNode(actionId, action);
                
                // Add any properties from the drag data
                if (dragData && dragData.properties && dragData.properties !== '{}') {
                    node.dataset.properties = dragData.properties;
                    updateNodeDisplay(node);
                }
                
                // Add to canvas at proper position
                const afterElement = getActionDragAfterElement(canvas, e.clientY);
                if (afterElement) {
                    canvas.insertBefore(node, afterElement);
                } else {
                    canvas.appendChild(node);
                }
            }
        }
        else {
            console.log('No recognized drag data, using legacy format');
            // Handle legacy format or unknown data
            if (data === 'screen_scope') {
                const placeholder = document.querySelector('.canvas-placeholder');
                if (placeholder) {
                    placeholder.remove();
                }
                
                const node = createScreenScopeNode({
                    name: 'New Screen Scope',
                    csv_path: ''
                });
                canvas.appendChild(node);
                
                // Force the scope container to be fully visible
                const scopeContent = node.querySelector('.scope-content');
                const scopePreview = node.querySelector('.scope-preview');
                if (scopeContent) scopeContent.style.display = 'block';
                if (scopePreview) scopePreview.style.display = 'block';
                
                // Ensure placeholder visibility is updated
                updatePlaceholderVisibility();
            } else if (data) { // Check if data exists
                const action = actions[data];
                if (!action) {
                    console.error('Action not found:', data);
                    return;
                }
                
                // Handle drops directly on the canvas or in a scope
                const scopeContent = e.target.closest('.scope-actions-container');
                if (scopeContent) {
                    const actionNode = createActionNode(data, action);
                    scopeContent.appendChild(actionNode);
                } else {
                    const node = createActionNode(data, action);
                    canvas.appendChild(node);
                }
            } else {
                console.error('No action ID found in drop data');
            }
        }
        
        updateAllOrderNumbers();
        document.querySelector('.dragging')?.classList.remove('dragging');
        document.querySelector('.dragging-from-sidebar')?.classList.remove('dragging-from-sidebar');
    });
    
    // Add event delegation for scope content areas
    document.addEventListener('dragover', (e) => {
        if (e.target.classList.contains('scope-actions-container') || e.target.closest('.scope-actions-container')) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        }
    });
    
    // Initialize newly created nodes
    reinitializeDragAndDrop();
}

function createScreenScopeNode(scopeData) {
    const node = document.createElement('div');
    node.className = 'action-node screen-scope-node';
    // Explicitly ensure it's not minimized on creation
    node.classList.remove('minimized');
    node.dataset.type = 'scope';
    node.dataset.name = scopeData.name;
    node.dataset.csvPath = scopeData.csv_path;
    node.draggable = true;  // Make screen scopes draggable
    
    // Store original properties to ensure they're not lost during rearrangement
    if (!node.dataset.properties && scopeData.actions) {
        node.dataset.properties = JSON.stringify({
            name: scopeData.name,
            csv_path: scopeData.csv_path,
            actions: scopeData.actions
        });
    }
    
    // Add drag event listeners only to screen scopes
    node.addEventListener('dragstart', handleDragStart);
    node.addEventListener('dragend', handleDragEnd);
    node.addEventListener('dragover', handleDragOver);
    node.addEventListener('drop', handleDrop);
    
    // Add order box
    const orderBox = document.createElement('div');
    orderBox.className = 'order-box';
    orderBox.textContent = getNodeOrder(node);
    
    // Create content wrapper
    const content = document.createElement('div');
    content.className = 'action-node-content';
    
    const header = document.createElement('div');
    header.className = 'd-flex align-items-center justify-content-between';
    
    // Left section of header with title
    const headerLeft = document.createElement('div');
    headerLeft.className = 'd-flex align-items-center';
    
    // Add minimize button
    const minimizeBtn = document.createElement('button');
    minimizeBtn.className = 'btn btn-sm btn-outline-secondary me-2';
    minimizeBtn.innerHTML = '<i class="fas fa-minus"></i>'; // Start with minus icon (not minimized)
    minimizeBtn.onclick = (e) => {
        e.stopPropagation();
        toggleMinimize(node);
    };
    
    const title = document.createElement('h5');
    title.className = 'mb-0';
    title.innerHTML = `<i class="fas fa-desktop"></i> Screen Scope: ${scopeData.name}`;
    
    headerLeft.appendChild(minimizeBtn);
    headerLeft.appendChild(title);
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn btn-sm btn-danger';
    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
    deleteBtn.onclick = (e) => {
        e.stopPropagation();
        node.remove();
        updateAllOrderNumbers();
    };
    
    header.appendChild(headerLeft);
    header.appendChild(deleteBtn);
    content.appendChild(header);
    
    // Add preview image
    const preview = document.createElement('div');
    preview.className = 'scope-preview';
    preview.style.display = 'block'; // Ensure preview is visible
    const img = document.createElement('img');
    
    // Always start with placeholder until real image is loaded
    img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDIwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjIwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNlOWVjZWYiLz48dGV4dCB4PSI0MCIgeT0iNTAiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzZjNzU3ZCI+TmVlZHMgc2NyZWVuIHNlbGVjdGlvbjwvdGV4dD48L3N2Zz4=';
    
    // Try to load an actual image if a name is provided
    if (scopeData.name && scopeData.name !== 'New Screen Scope') {
        const actualImg = new Image();
        actualImg.onload = function() {
            img.src = this.src;
        };
        actualImg.src = `/api/output/${scopeData.name}_parsed.png`;
    }
    
    img.className = 'preview-image';
    preview.appendChild(img);
    content.appendChild(preview);
    
    // Add container for actions
    const scopeContent = document.createElement('div');
    scopeContent.className = 'scope-content';
    scopeContent.style.display = 'block'; // Ensure content is visible
    
    // Create a wrapper for the placeholder
    const placeholderWrapper = document.createElement('div');
    placeholderWrapper.className = 'scope-placeholder-wrapper';
    const placeholder = document.createElement('div');
    placeholder.className = 'canvas-placeholder';
    placeholder.textContent = 'Drag actions here';
    placeholderWrapper.appendChild(placeholder);
    
    // Create a container for the actual actions
    const actionsContainer = document.createElement('div');
    actionsContainer.className = 'scope-actions-container';
    
    // Add custom attribute to prevent event conflicts
    actionsContainer.dataset.containerType = 'scope-actions';
    
    // Add direct event handlers to the actions container
    actionsContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        actionsContainer.classList.add('drag-over');
        
        // Only allow action nodes (not screen scopes)
        const draggingNode = document.querySelector('.dragging');
        if (draggingNode && !draggingNode.classList.contains('screen-scope-node')) {
            e.dataTransfer.dropEffect = 'move';
            
            // Hide placeholder when hovering over the container
            if (placeholder) {
                placeholder.style.opacity = '0.3';
            }
            
            // Show drop indicator
            const afterElement = getActionDragAfterElement(actionsContainer, e.clientY);
            document.querySelectorAll('.drop-indicator').forEach(el => el.remove());
            
            const indicator = document.createElement('div');
            indicator.className = 'drop-indicator';
            
            if (afterElement) {
                actionsContainer.insertBefore(indicator, afterElement);
            } else {
                actionsContainer.appendChild(indicator);
            }
        }
    });
    
    actionsContainer.addEventListener('dragleave', (e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) {
            actionsContainer.classList.remove('drag-over');
            
            // Show placeholder again for empty containers
            if (actionsContainer.children.length === 0 && placeholder) {
                placeholder.style.opacity = '1';
            }
            
            // Remove indicator
            document.querySelectorAll('.drop-indicator').forEach(el => el.remove());
        }
    });
    
    actionsContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('Drop on actions container');
        
        // Handle the drop
        dropActionOnContainer(e, actionsContainer);
    });
    
    // Add direct event handlers to the placeholder
    placeholder.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const actionsContainer = scopeContent.querySelector('.scope-actions-container');
        actionsContainer.classList.add('drag-over');
        placeholder.style.opacity = '0.3';
        
        // Check if we're dragging an action node
        const draggingNode = document.querySelector('.dragging');
        if (draggingNode && !draggingNode.classList.contains('screen-scope-node')) {
            e.dataTransfer.dropEffect = 'copy';
        }
    });
    
    placeholder.addEventListener('dragleave', (e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) {
            const actionsContainer = scopeContent.querySelector('.scope-actions-container');
            actionsContainer.classList.remove('drag-over');
            placeholder.style.opacity = '1';
        }
    });
    
    placeholder.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('Drop on placeholder');
        
        // Forward the drop event to the action container
        const actionsContainer = scopeContent.querySelector('.scope-actions-container');
        
        // Reset visual state
        actionsContainer.classList.remove('drag-over');
        placeholder.style.opacity = '1';
        
        // Handle the drop
        dropActionOnContainer(e, actionsContainer);
    });
    
    scopeContent.appendChild(actionsContainer);
    scopeContent.appendChild(placeholderWrapper);
    
    content.appendChild(scopeContent);
    node.appendChild(orderBox);
    node.appendChild(content);
    
    // Add click handler for node selection
    node.onclick = (e) => {
        if (!node.classList.contains('minimized')) {
            selectNode(node, { name: 'Screen Scope', parameters: [] });
        }
    };
    
    // Initialize the node's drag and drop handlers
    reinitializeDragAndDrop();
    
    return node;
}

function createActionNode(actionId, action) {
    const node = document.createElement('div');
    node.className = 'action-node';
    node.dataset.actionId = actionId;
    node.draggable = true;  // Make action nodes draggable as well
    
    // Add drag event listeners
    node.addEventListener('dragstart', handleActionDragStart);
    node.addEventListener('dragend', handleActionDragEnd);
    node.addEventListener('dragover', handleActionDragOver);
    node.addEventListener('drop', handleActionDrop);
    
    // Add order box
    const orderBox = document.createElement('div');
    orderBox.className = 'order-box';
    orderBox.textContent = getNodeOrder(node);
    
    // Create content wrapper
    const content = document.createElement('div');
    content.className = 'action-node-content';
    
    const header = document.createElement('div');
    header.className = 'd-flex align-items-center justify-content-between';
    
    const title = document.createElement('h5');
    title.className = 'mb-0';
    title.textContent = action.name;
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn btn-sm btn-danger';
    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
    deleteBtn.onclick = (e) => {
        e.stopPropagation();
        node.remove();
        updateAllOrderNumbers();
    };
    
    header.appendChild(title);
    header.appendChild(deleteBtn);
    content.appendChild(header);
    
    node.appendChild(orderBox);
    node.appendChild(content);
    
    node.onclick = (e) => {
        e.stopPropagation();
        selectNode(node, action);
    };
    
    return node;
}

function getNodeOrder(node) {
    const isInScope = node.closest('.screen-scope-node');
    const parent = isInScope ? node.closest('.screen-scope-node') : document.getElementById('canvas');
    
    // Get all siblings that are action nodes
    const siblings = Array.from(parent.children).filter(child => {
        // For screen scopes, only count other screen scopes
        if (node.classList.contains('screen-scope-node')) {
            return child.classList.contains('screen-scope-node');
        }
        // For regular actions, only count other actions within the same scope
        return child.classList.contains('action-node') && 
               (!isInScope || child.closest('.screen-scope-node') === isInScope);
    });
    
    return siblings.indexOf(node) + 1;
}

function updateAllOrderNumbers() {
    // Update screen scope nodes
    const screenScopeNodes = document.querySelectorAll('.screen-scope-node');
    screenScopeNodes.forEach((node, index) => {
        const orderBox = node.querySelector('.order-box');
        orderBox.textContent = index + 1;
    });

    // Update action nodes in the main canvas
    const actionNodes = Array.from(document.querySelectorAll('#canvas > .action-node'));
    actionNodes.forEach((node, index) => {
        const orderBox = node.querySelector('.order-box');
        orderBox.textContent = index + 1;
    });

    // Update action nodes within each screen scope
    const scopeContainers = document.querySelectorAll('.scope-actions-container');
    scopeContainers.forEach(container => {
        const actionsInScope = Array.from(container.querySelectorAll('.action-node'));
        actionsInScope.forEach((node, index) => {
            const orderBox = node.querySelector('.order-box');
            orderBox.textContent = index + 1;
        });
    });
    
    // Save the script after updating order numbers, but silently (without alerts)
    saveScript(true);
}

function selectNode(node, action) {
    if (selectedNode) {
        selectedNode.classList.remove('selected');
    }
    
    node.classList.add('selected');
    selectedNode = node;
    
    const form = document.getElementById('propertiesForm');
    form.innerHTML = '';
    
    if (node.dataset.type === 'scope' || node.dataset.actionId === 'screen_scope') {
        // Create screen scope gallery in properties panel
        const gallery = document.createElement('div');
        gallery.id = 'scopeGallery';
        gallery.className = 'scope-gallery';
        
        // Load screen scopes
        fetch('/api/parsed_images')
            .then(response => response.json())
            .then(parsedImages => {
                parsedImages.forEach(image => {
                    const scopeItem = document.createElement('div');
                    scopeItem.className = 'scope-item';
                    if (node.dataset.name === image.name) {
                        scopeItem.classList.add('selected');
                    }
                    
                    const img = document.createElement('img');
                    img.src = `/api/output/${image.name}_parsed.png`;
                    img.className = 'scope-image';
                    img.alt = image.name;
                    
                    const name = document.createElement('p');
                    name.className = 'scope-name';
                    name.textContent = image.name;
                    
                    scopeItem.appendChild(img);
                    scopeItem.appendChild(name);
                    
                    scopeItem.onclick = () => {
                        // Update the screen scope node
                        node.dataset.name = image.name;
                        node.dataset.csvPath = image.csv_path;
                        const title = node.querySelector('h5');
                        title.innerHTML = `<i class="fas fa-desktop"></i> Screen Scope: ${image.name}`;
                        
                        // Update preview image
                        const previewImg = node.querySelector('.preview-image');
                        previewImg.src = `/api/output/${image.name}_parsed.png`;
                        
                        // Update selection
                        document.querySelectorAll('.scope-item').forEach(item => item.classList.remove('selected'));
                        scopeItem.classList.add('selected');
                    };
                    
                    gallery.appendChild(scopeItem);
                });
            })
            .catch(error => console.error('Error loading screen scopes:', error));
        
        form.appendChild(gallery);
    } else {
    updatePropertiesForm(action);
    }
}

function updatePropertiesForm(action) {
    const form = document.getElementById('propertiesForm');
    form.innerHTML = '';
    
    if (!action.parameters || action.parameters.length === 0) {
        form.innerHTML = '<div class="alert alert-info">No properties to configure</div>';
        return;
    }
    
    const formElement = document.createElement('form');
    formElement.className = 'needs-validation';
    
    // Get existing properties
    const existingProperties = selectedNode ? JSON.parse(selectedNode.dataset.properties || '{}') : {};
    
    action.parameters.forEach(param => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';
        
        const label = document.createElement('label');
        label.className = 'form-label';
        label.textContent = param.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        if (param === 'csv_file') {
            const select = document.createElement('select');
            select.className = 'form-select';
            select.name = param;
            
            // Find the parent screen scope if this action is inside one
            const parentScope = selectedNode.closest('.screen-scope-node');
            if (parentScope) {
                const scopeOption = document.createElement('option');
                scopeOption.value = parentScope.dataset.csvPath;
                scopeOption.textContent = `Current Scope (${parentScope.dataset.name})`;
                select.appendChild(scopeOption);
            } else if (currentScope) {
                const scopeOption = document.createElement('option');
                scopeOption.value = currentScope.csv_path;
                scopeOption.textContent = `Current Scope (${currentScope.name})`;
                select.appendChild(scopeOption);
            }
            
            bboxFiles.forEach(file => {
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                select.appendChild(option);
            });
            
            formGroup.appendChild(label);
            formGroup.appendChild(select);
        } else if (param === 'click_before') {
            const checkbox = document.createElement('div');
            checkbox.className = 'form-check';
            
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.className = 'form-check-input';
            input.name = param;
            
            const label = document.createElement('label');
            label.className = 'form-check-label';
            label.textContent = 'Click before action';
            
            checkbox.appendChild(input);
            checkbox.appendChild(label);
            formGroup.appendChild(checkbox);
        } else {
            formGroup.appendChild(label);
            const input = document.createElement('input');
            input.className = 'form-control';
            input.name = param;
            
            // Set default value of 0 for x_offset and y_offset if not set
            if ((param === 'x_offset' || param === 'y_offset') && !existingProperties[param]) {
                input.value = '0';
            } else if (existingProperties[param]) {
                input.value = existingProperties[param];
            }
            
            formGroup.appendChild(input);
        }
        
        formElement.appendChild(formGroup);
    });
    
    const saveBtn = document.createElement('button');
    saveBtn.type = 'submit';
    saveBtn.className = 'btn btn-primary mt-3';
    saveBtn.textContent = 'Save Properties';
    saveBtn.onclick = (e) => {
        e.preventDefault();
        saveNodeProperties(formElement);
    };
    
    formElement.appendChild(saveBtn);
    form.appendChild(formElement);
}

function saveNodeProperties(form) {
    if (!selectedNode) return;
    
    const formData = new FormData(form);
    const properties = {};
    
    for (const [key, value] of formData.entries()) {
        properties[key] = value;
    }
    
    selectedNode.dataset.properties = JSON.stringify(properties);
    
    // Update node display using the updateNodeDisplay function
    updateNodeDisplay(selectedNode);
}

function initializeSaveButton() {
    const saveBtn = document.getElementById('saveScript');
    saveBtn.onclick = () => saveScript(false);
}

function initializePlayButton() {
    const playBtn = document.getElementById('playScript');
    const stopBtn = document.getElementById('stopScript');
    
    playBtn.onclick = playScript;
    stopBtn.onclick = stopScript;
    
    // Initially hide the stop button
    stopBtn.style.display = 'none';
}

function updateNodeDisplay(node) {
    const actionId = node.dataset.actionId;
    const action = actions[actionId];
    const properties = JSON.parse(node.dataset.properties || '{}');
    console.log('Updating node display for action:', actionId, 'with properties:', properties);
    
    const title = node.querySelector('h5');
    
    // Create a more readable display of properties
    const propertyDisplay = Object.entries(properties)
        .map(([key, value]) => {
            console.log(`Property ${key}:`, value);
            if (key === 'csv_file') {
                return `CSV: ${value.split('/').pop()}`;
            }
            if (key === 'click_before') {
                return value === 'on' ? 'Click Before' : '';
            }
            if (key === 'x_offset' || key === 'y_offset') {
                return `${key}: ${value}`;
            }
            if (key === 'bbox_id') {
                console.log('Found bbox_id:', value);
                return `BBox: ${value}`;
            }
            return value;
        })
        .filter(Boolean)
        .join(', ');
    
    console.log('Final property display:', propertyDisplay);
    title.textContent = propertyDisplay ? `${action.name} (${propertyDisplay})` : action.name;
}

async function saveScript(silent = false) {
    const scriptName = document.getElementById('scriptName').value;
    if (!scriptName) {
        if (!silent) {
            showToast('Please enter a script name', 'error');
        }
        return;
    }
    
    const nodes = document.querySelectorAll('.action-node');
    const actions = Array.from(nodes).map(node => {
        if (node.dataset.type === 'scope') {
            // Get all actions within this scope
            const scopeActions = Array.from(node.querySelectorAll('.scope-content .action-node')).map(actionNode => ({
                id: actionNode.dataset.actionId,
                properties: JSON.parse(actionNode.dataset.properties || '{}')
            }));
            
            return {
                id: 'screen_scope',
                properties: {
                    name: node.dataset.name,
                    csv_path: node.dataset.csvPath,
                    actions: scopeActions
                }
            };
        } else if (!node.closest('.screen-scope-node')) {
            // Only include top-level actions (not inside a scope)
            return {
        id: node.dataset.actionId,
        properties: JSON.parse(node.dataset.properties || '{}')
            };
        }
        return null;
    }).filter(action => action !== null);
    
    try {
        const response = await fetch('/api/save_script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: scriptName,
                actions: actions
            })
        });
        
        const result = await response.json();
        if (response.ok) {
            // Only show the notification if not in silent mode
            if (!silent) {
                showToast(`Script "${scriptName}" saved successfully!`, 'success');
            }
        } else {
            // Always show errors, even in silent mode
            showToast(`Error saving script: ${result.error}`, 'error', 5000);
        }
    } catch (error) {
        console.error('Error saving script:', error);
        // Always show errors, even in silent mode
        showToast('Error saving script. Check console for details.', 'error', 5000);
    }
}

async function playScript() {
    const scriptName = document.getElementById('scriptName').value;
    if (!scriptName) {
        alert('Please enter a script name');
        return;
    }
    
    const playBtn = document.getElementById('playScript');
    const stopBtn = document.getElementById('stopScript');
    const outputPanel = document.getElementById('scriptOutput');
    
    if (isPlaying) {
        return;
    }
    
    isPlaying = true;
    playBtn.disabled = true;
    playBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Playing...';
    // Show the stop button when playing
    stopBtn.style.display = 'inline-block';
    outputPanel.textContent = 'Executing script...\n';
    
    try {
        console.log(`Executing script: ${scriptName}`);
        const response = await fetch('/api/play_script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: scriptName
            })
        });
        
        const result = await response.json();
        console.log("API response:", result);
        
        if (response.ok) {
            // Script executed successfully
            outputPanel.textContent += result.output || '';
            if (result.error && result.error.trim()) {
                outputPanel.textContent += '\n\nWarnings/Messages:\n' + result.error;
            }
            outputPanel.textContent += '\n\nScript execution completed successfully.';
        } else {
            // Script execution failed
            outputPanel.textContent += '\n\nError: ' + result.error;
            
            // Add error analysis if available
            if (result.error_analysis && result.error_analysis.length > 0) {
                outputPanel.textContent += '\n\nError Analysis:';
                result.error_analysis.forEach(item => {
                    outputPanel.textContent += '\n• ' + item;
                });
            }
            
            // Add detailed traceback information if available
            if (result.traceback) {
                outputPanel.textContent += '\n\nError Details:\n' + result.traceback;
            }
            
            // Add detailed error message if available
            if (result.details) {
                outputPanel.textContent += '\n\nDetails: ' + result.details;
            }
            
            // Add error_output if it exists (different from regular error)
            if (result.error_output && result.error_output.trim() && (!result.error || result.error_output !== result.error)) {
                outputPanel.textContent += '\n\nError Output:\n' + result.error_output;
            }
            
            // Add output for context
            if (result.output && result.output.trim()) {
                outputPanel.textContent += '\n\nScript Output:\n' + result.output;
            } else if (result.error && result.error.trim()) {
                outputPanel.textContent += '\n\nScript Errors:\n' + result.error;
            }
            
            outputPanel.textContent += '\n\nScript execution failed. Check the error details above for more information.';
            
            // Add troubleshooting suggestions
            outputPanel.textContent += '\n\nTroubleshooting Suggestions:';
            outputPanel.textContent += '\n• Verify that the hardware is properly connected';
            outputPanel.textContent += '\n• Ensure the CSV files exist in the output directory';
            outputPanel.textContent += '\n• Check that the COM port matches your hardware';
            outputPanel.textContent += '\n• Try restarting the hardware and rerunning the script';
        }
        
        // Scroll to the bottom of the output panel
        outputPanel.scrollTop = outputPanel.scrollHeight;
    } catch (error) {
        console.error('Error playing script:', error);
        outputPanel.textContent += '\n\nNetwork Error: ' + error.message + '\n\n';
        outputPanel.textContent += 'There was a problem communicating with the server. Please try again later.';
        
        // Add troubleshooting suggestions for network errors
        outputPanel.textContent += '\n\nTroubleshooting Suggestions:';
        outputPanel.textContent += '\n• Check your network connection';
        outputPanel.textContent += '\n• Verify the server is running';
        outputPanel.textContent += '\n• Try refreshing the page and running the script again';
    } finally {
        isPlaying = false;
        playBtn.disabled = false;
        playBtn.innerHTML = '<i class="fas fa-play"></i> Play';
        // Hide the stop button when done
        stopBtn.style.display = 'none';
        // Scroll to the bottom of the output panel
        outputPanel.scrollTop = outputPanel.scrollHeight;
    }
}

async function stopScript() {
    if (!isPlaying) {
        return;
    }
    
    const stopBtn = document.getElementById('stopScript');
    const outputPanel = document.getElementById('scriptOutput');
    
    // Disable the stop button and show loading state
    stopBtn.disabled = true;
    stopBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Stopping...';
    outputPanel.textContent += '\nStopping script...\n';
    
    try {
        const response = await fetch('/api/stop_script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            outputPanel.textContent += 'Script stopped successfully.\n';
            if (result.output) {
                outputPanel.textContent += '\nOutput: ' + result.output + '\n';
            }
            if (result.error) {
                outputPanel.textContent += '\nErrors: ' + result.error + '\n';
            }
        } else {
            outputPanel.textContent += 'Error stopping script: ' + result.error + '\n';
        }
    } catch (error) {
        console.error('Error stopping script:', error);
        outputPanel.textContent += 'Error stopping script: ' + error.message + '\n';
    } finally {
        // Reset the play/stop buttons
        isPlaying = false;
        const playBtn = document.getElementById('playScript');
        playBtn.disabled = false;
        playBtn.innerHTML = '<i class="fas fa-play"></i> Play';
        
        // Hide the stop button
        stopBtn.disabled = false;
        stopBtn.style.display = 'none';
    }
}

// Function to toggle minimize/maximize state of a screen scope
function toggleMinimize(node) {
    if (node.classList.contains('minimized')) {
        // Maximize
        node.classList.remove('minimized');
        const minimizeBtn = node.querySelector('.btn-outline-secondary');
        if (minimizeBtn) {
            minimizeBtn.innerHTML = '<i class="fas fa-minus"></i>';
        }
        // Explicitly show content
        const scopeContent = node.querySelector('.scope-content');
        const scopePreview = node.querySelector('.scope-preview');
        if (scopeContent) scopeContent.style.display = 'block';
        if (scopePreview) scopePreview.style.display = 'block';
    } else {
        // Minimize
        node.classList.add('minimized');
        const minimizeBtn = node.querySelector('.btn-outline-secondary');
        if (minimizeBtn) {
            minimizeBtn.innerHTML = '<i class="fas fa-plus"></i>';
        }
        // Explicitly hide content
        const scopeContent = node.querySelector('.scope-content');
        const scopePreview = node.querySelector('.scope-preview');
        if (scopeContent) scopeContent.style.display = 'none';
        if (scopePreview) scopePreview.style.display = 'none';
    }
}

// Update drag handlers to only work with screen scopes
function handleDragStart(e) {
    if (!e.target.classList.contains('screen-scope-node')) return;
    e.target.classList.add('dragging');
    e.dataTransfer.setData('text/plain', 'screen_scope');
    e.dataTransfer.setData('application/json', JSON.stringify({
        type: 'screen_scope',
        name: e.target.dataset.name || 'Unnamed Scope',
        csvPath: e.target.dataset.csvPath || ''
    }));
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation(); // Prevent event bubbling to parent handlers
    console.log("Screen scope drag over event");
    
    const draggingNode = document.querySelector('.dragging');
    if (!draggingNode || !draggingNode.classList.contains('screen-scope-node')) return;
    
    // Only allow dropping on the main canvas
    const canvas = document.getElementById('canvas');
    
    // Only move the node if we're actually dragging something
    if (draggingNode && draggingNode.parentNode === canvas) {
        const afterElement = getDragAfterElement(canvas, e.clientY);
        
        // Visualize the potential drop position with an indicator
        document.querySelectorAll('.scope-drop-indicator').forEach(el => el.remove());
        if (afterElement) {
            console.log("Would insert screen scope before:", afterElement.dataset.name || 'unnamed');
            
            // Create a position indicator
            const indicator = document.createElement('div');
            indicator.className = 'scope-drop-indicator';
            indicator.style.height = '2px';
            indicator.style.backgroundColor = '#28a745'; // Green for screen scopes
            indicator.style.margin = '2px 0';
            indicator.style.width = '100%';
            indicator.style.position = 'relative';
            indicator.style.zIndex = '1000';
            
            canvas.insertBefore(indicator, afterElement);
        } else if (canvas.children.length > 0) {
            console.log("Would append screen scope to end of canvas");
            
            // Create a position indicator at the end
            const indicator = document.createElement('div');
            indicator.className = 'scope-drop-indicator';
            indicator.style.height = '2px';
            indicator.style.backgroundColor = '#28a745'; // Green for screen scopes
            indicator.style.margin = '2px 0';
            indicator.style.width = '100%';
            indicator.style.position = 'relative';
            indicator.style.zIndex = '1000';
            
            canvas.appendChild(indicator);
        }
    }
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation(); // Prevent event bubbling to action handlers
    console.log("Screen scope drop event");
    
    // Clean up indicators
    document.querySelectorAll('.scope-drop-indicator').forEach(el => el.remove());
    
    // Find the dragging element
    const draggingNode = document.querySelector('.dragging');
    if (!draggingNode || !draggingNode.classList.contains('screen-scope-node')) return;
    
    // Only allow dropping on the main canvas
    const canvas = document.getElementById('canvas');
    
    // Get the position to insert before
    const afterElement = getDragAfterElement(canvas, e.clientY);
    
    // Move the node to the new position
    if (afterElement) {
        console.log("Inserting screen scope before:", afterElement.dataset.name || 'unnamed');
        canvas.insertBefore(draggingNode, afterElement);
    } else {
        console.log("Appending screen scope to canvas");
        canvas.appendChild(draggingNode);
    }
    
    // Remove dragging and highlight classes
    document.querySelectorAll('.dragging').forEach(el => el.classList.remove('dragging'));
    document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
    
    updateAllOrderNumbers();
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.screen-scope-node:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// Update CSS to show grab cursor on both screen scopes and action nodes and add drop indicators
const style = document.createElement('style');
style.textContent = `
    .screen-scope-node.dragging, .action-node.dragging {
        opacity: 0.5;
        cursor: grabbing;
    }
    .screen-scope-node, .action-node {
        cursor: grab;
    }
    .screen-scope-node:hover, .action-node:hover {
        cursor: grab;
    }
    .action-item.dragging {
        opacity: 0.5;
    }
    .action-item {
        cursor: grab;
    }
    .drag-over {
        border: 2px dashed #007bff !important;
        background-color: rgba(0, 123, 255, 0.1);
    }
    #canvas.drag-over {
        background-color: rgba(40, 167, 69, 0.1) !important;
        border: 2px dashed #28a745 !important;
    }
    .scope-actions-container.drag-over {
        background-color: rgba(0, 123, 255, 0.1) !important;
        border: 2px dashed #007bff !important;
        min-height: 60px; /* Ensure empty containers have height */
    }
    .scope-actions-container {
        min-height: 40px; /* Minimum height for drop target */
        position: relative;
    }
    .scope-actions-container:empty {
        display: block !important; /* Force display even when empty */
    }
    .scope-content {
        position: relative;
    }
    .scope-placeholder-wrapper {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none; /* Let events pass through to container */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .scope-placeholder-wrapper .canvas-placeholder {
        pointer-events: auto; /* Allow interactions with placeholder */
        width: 100%;
        text-align: center;
        padding: 10px;
        color: #6c757d;
        font-style: italic;
        background-color: transparent;
    }
    .drop-indicator {
        height: 2px;
        background-color: #007bff;
        margin: 4px 0;
        width: 100%;
        position: relative;
        z-index: 1000;
        animation: pulse 1.5s infinite;
    }
    .scope-drop-indicator {
        height: 2px;
        background-color: #28a745;
        margin: 4px 0;
        width: 100%;
        position: relative;
        z-index: 1000;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
`;
document.head.appendChild(style);

// Add function to enhance drag-and-drop visual feedback
function setupDragAndDropVisualFeedback() {
    const canvas = document.getElementById('canvas');
    
    // Add dragenter and dragleave for canvas
    canvas.addEventListener('dragenter', (e) => {
        e.preventDefault();
        canvas.classList.add('drag-over');
    });
    
    canvas.addEventListener('dragleave', (e) => {
        e.preventDefault();
        if (!e.currentTarget.contains(e.relatedTarget)) {
            canvas.classList.remove('drag-over');
        }
    });
    
    canvas.addEventListener('drop', () => {
        canvas.classList.remove('drag-over');
    });
    
    // Set up delegation for scope content containers
    document.addEventListener('dragenter', (e) => {
        if (e.target.classList.contains('scope-actions-container')) {
            e.preventDefault();
            e.target.classList.add('drag-over');
        }
    });
    
    document.addEventListener('dragleave', (e) => {
        if (e.target.classList.contains('scope-actions-container') && 
            !e.currentTarget.contains(e.relatedTarget)) {
            e.preventDefault();
            e.target.classList.remove('drag-over');
        }
    });
    
    document.addEventListener('drop', (e) => {
        const container = e.target.closest('.scope-actions-container');
        if (container) {
            container.classList.remove('drag-over');
        }
    });
}

// Handlers for action node dragging
function handleActionDragStart(e) {
    e.target.classList.add('dragging');
    // Store the node's parent to know where it came from
    e.target.dataset.originalParent = e.target.parentElement.id || e.target.parentElement.className;
    // Set the action ID as the data
    e.dataTransfer.setData('text/plain', e.target.dataset.actionId);
    e.dataTransfer.setData('application/json', JSON.stringify({
        type: 'action',
        actionId: e.target.dataset.actionId,
        properties: e.target.dataset.properties || '{}'
    }));
    e.dataTransfer.effectAllowed = 'move';
}

function handleActionDragEnd(e) {
    e.target.classList.remove('dragging');
    delete e.target.dataset.originalParent;
    
    // Trigger silent save on drag end to persist changes without alerts
    saveScript(true);
}

function handleActionDragOver(e) {
    e.preventDefault();
    e.stopPropagation(); // Stop event bubbling to parent handlers
    console.log("Action drag over event:", e.target.className);
    
    // Find the dragging node
    const draggingNode = document.querySelector('.dragging');
    if (!draggingNode) return;
    
    // If it's a screen scope being dragged, let the screen scope handler work instead
    if (draggingNode.classList.contains('screen-scope-node')) {
        e.dataTransfer.dropEffect = 'none'; // Indicate that dropping is not allowed here
        return;
    }
    
    e.dataTransfer.dropEffect = 'move';
    
    // Determine the target container (either canvas or scope-actions-container)
    let targetContainer;
    if (e.target.classList.contains('scope-actions-container')) {
        targetContainer = e.target;
    } else if (e.target.closest('.scope-actions-container')) {
        targetContainer = e.target.closest('.scope-actions-container');
    } else if (e.target.classList.contains('canvas-placeholder') && e.target.closest('.scope-content')) {
        // Handle drag over placeholders in empty screen scopes
        targetContainer = e.target.closest('.scope-content').querySelector('.scope-actions-container');
    } else if (e.target.id === 'canvas' || e.target.closest('#canvas')) {
        // Only accept direct canvas drops if we're not inside a screen scope already
        const canvas = document.getElementById('canvas');
        if (!draggingNode.closest('.screen-scope-node')) {
            targetContainer = canvas;
        }
    }
    
    if (!targetContainer) return;
    
    console.log(`Dragging action node ${draggingNode.dataset.actionId || 'unknown'} over container:`, 
               targetContainer.id || targetContainer.className);
    
    // Clear all existing indicators first
    document.querySelectorAll('.drop-indicator').forEach(el => el.remove());
    
    // Find where to insert the node
    const afterElement = getActionDragAfterElement(targetContainer, e.clientY);
    
    // Visualize the potential drop position
    if (afterElement) {
        console.log("Would insert action before:", afterElement.dataset.actionId || 'unknown');
        
        // Create a position indicator
        const indicator = document.createElement('div');
        indicator.className = 'drop-indicator';
        indicator.style.height = '2px';
        indicator.style.backgroundColor = '#007bff';
        indicator.style.margin = '2px 0';
        indicator.style.width = '100%';
        indicator.style.position = 'relative';
        indicator.style.zIndex = '1000';
        
        targetContainer.insertBefore(indicator, afterElement);
    } else {
        console.log("Would append action to container");
        
        // Create a position indicator at the end - works for both empty and non-empty containers
        const indicator = document.createElement('div');
        indicator.className = 'drop-indicator';
        indicator.style.height = '2px';
        indicator.style.backgroundColor = '#007bff';
        indicator.style.margin = '2px 0';
        indicator.style.width = '100%';
        indicator.style.position = 'relative';
        indicator.style.zIndex = '1000';
        
        targetContainer.appendChild(indicator);
    }
}

function handleActionDrop(e) {
    e.preventDefault();
    e.stopPropagation(); // Stop event bubbling to parent handlers
    console.log("Action drop event occurred");
    
    // Clean up indicators
    document.querySelectorAll('.drop-indicator').forEach(el => el.remove());
    
    // Find the dragging element
    const draggingNode = document.querySelector('.dragging');
    if (!draggingNode) return;
    
    // If it's a screen scope, let the screen scope handler work instead
    if (draggingNode.classList.contains('screen-scope-node')) {
        console.log("Ignoring screen scope in action drop handler");
        return;
    }
    
    // Get the dragged data
    const dragDataStr = e.dataTransfer.getData('application/json');
    let dragData;
    try {
        if (dragDataStr) {
            dragData = JSON.parse(dragDataStr);
        }
    } catch (error) {
        console.error('Error parsing drag data:', error);
    }
    
    // Determine the drop target container
    let container = e.target;
    
    // Handle drops on placeholders in screen scopes
    if (e.target.classList.contains('canvas-placeholder') && e.target.closest('.scope-content')) {
        container = e.target.closest('.scope-content').querySelector('.scope-actions-container');
    } else {
        // Standard container detection
        while (container && !container.classList.contains('scope-actions-container') && container.id !== 'canvas') {
            container = container.parentElement;
        }
    }
    
    if (!container) {
        container = document.getElementById('canvas');
    }
    
    console.log("Drop container:", container.id || container.className);
    
    // Reset any hidden placeholders
    document.querySelectorAll('.canvas-placeholder').forEach(placeholder => {
        placeholder.style.visibility = '';
    });
    
    // If we're dragging from the sidebar (creating a new node)
    if (document.querySelector('.dragging-from-sidebar') || 
        (dragData && dragData.fromSidebar)) {
        console.log("Creating new node from sidebar");
        if (dragData && dragData.type === 'action') {
            const action = actions[dragData.actionId];
            if (!action) {
                console.error('Action not found:', dragData.actionId);
                return;
            }
            
            console.log('Creating new action node:', dragData.actionId);
            const node = createActionNode(dragData.actionId, action);
            
            // Add any properties from drag data
            if (dragData.properties && dragData.properties !== '{}') {
                node.dataset.properties = dragData.properties;
                updateNodeDisplay(node);
            }
            
            // Insert at the correct position
            const afterElement = getActionDragAfterElement(container, e.clientY);
            if (afterElement) {
                container.insertBefore(node, afterElement);
            } else {
                container.appendChild(node);
            }
        }
    } 
    // Otherwise if we're just moving an existing node
    else if (draggingNode.classList.contains('action-node')) {
        console.log("Moving existing action node");
        
        // Don't allow dragging between different scope types without explicit approval
        const sourceIsScope = draggingNode.closest('.screen-scope-node') !== null;
        const targetIsScope = container.closest('.screen-scope-node') !== null;
        
        if ((sourceIsScope && !targetIsScope) || (!sourceIsScope && targetIsScope)) {
            console.log('Moving between different container types');
        }
        
        // Get the position to insert
        const afterElement = getActionDragAfterElement(container, e.clientY);
        
        // Move the node to the new position
        if (afterElement) {
            console.log("Inserting action before:", afterElement.dataset.actionId || 'unknown');
            container.insertBefore(draggingNode, afterElement);
        } else {
            console.log("Appending action to container");
            container.appendChild(draggingNode);
        }
    }
    
    // Reset dragging state
    document.querySelectorAll('.dragging').forEach(el => el.classList.remove('dragging'));
    document.querySelectorAll('.dragging-from-sidebar').forEach(el => el.classList.remove('dragging-from-sidebar'));
    
    // Update visuals and save
    updatePlaceholderVisibility();
    updateAllOrderNumbers();
}

function getActionDragAfterElement(container, y) {
    // Get all draggable elements inside the container except the one being dragged
    const draggableElements = [...container.querySelectorAll('.action-node:not(.dragging):not(.drop-indicator)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// Update event delegation to properly handle scope containers
document.addEventListener('dragover', (e) => {
    // Handle scope content containers
    const scopeContainer = e.target.closest('.scope-actions-container');
    if (scopeContainer) {
        e.preventDefault();
        console.log('Delegated dragover on scope container');
        
        // Check if we're dragging an action node (not a screen scope)
        const draggingNode = document.querySelector('.dragging');
        if (draggingNode && !draggingNode.classList.contains('screen-scope-node')) {
            e.dataTransfer.dropEffect = 'move';
            scopeContainer.classList.add('drag-over');
        }
    }
    
    // Handle placeholder in scope content
    if (e.target.classList.contains('canvas-placeholder') && e.target.closest('.scope-content')) {
        e.preventDefault();
        console.log('Delegated dragover on scope placeholder');
        
        // Find the container
        const scopeContainer = e.target.closest('.scope-content').querySelector('.scope-actions-container');
        
        // Check if we're dragging an action node (not a screen scope)
        const draggingNode = document.querySelector('.dragging');
        if (draggingNode && !draggingNode.classList.contains('screen-scope-node')) {
            e.dataTransfer.dropEffect = 'move';
            scopeContainer.classList.add('drag-over');
            // Hide the placeholder during dragover to show the container behind it
            e.target.style.visibility = 'hidden';
        }
    }
    
    // Handle canvas container (for screen scopes)
    if (e.target.id === 'canvas' || e.target.closest('#canvas')) {
        e.preventDefault();
        
        // Check if we're dragging a screen scope
        const draggingNode = document.querySelector('.dragging');
        if (draggingNode && draggingNode.classList.contains('screen-scope-node')) {
            e.dataTransfer.dropEffect = 'move';
            document.getElementById('canvas').classList.add('drag-over');
        }
    }
});

// Update drop handling to clean up all visual indicators
document.addEventListener('drop', (e) => {
    // Remove all visual indicators
    document.querySelectorAll('.drop-indicator, .scope-drop-indicator').forEach(el => el.remove());
    document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
    
    // Reset any hidden placeholders
    document.querySelectorAll('.canvas-placeholder').forEach(placeholder => {
        placeholder.style.visibility = '';
    });
    
    // Special case for canvas drops
    if (e.target.id === 'canvas' || e.target.closest('#canvas')) {
        const draggingNode = document.querySelector('.dragging');
        if (draggingNode && draggingNode.classList.contains('screen-scope-node')) {
            // Let the screen scope handler take care of it
            console.log('Canvas drop detected for screen scope');
        }
    }
    
    // Update all dragging states
    const draggingElements = document.querySelectorAll('.dragging, .dragging-from-sidebar');
    if (draggingElements.length > 0) {
        console.log(`Clearing ${draggingElements.length} dragging elements`);
        draggingElements.forEach(el => {
            el.classList.remove('dragging');
            el.classList.remove('dragging-from-sidebar');
        });
    }
});

// Add a global function to initialize drag and drop on newly loaded nodes
function reinitializeDragAndDrop() {
    console.log("Reinitializing drag and drop handlers");
    
    // Reinitialize screen scope nodes
    const screenScopeNodes = document.querySelectorAll('.screen-scope-node');
    screenScopeNodes.forEach(node => {
        node.draggable = true;
        
        // Remove existing handlers to avoid duplicates
        node.removeEventListener('dragstart', handleDragStart);
        node.removeEventListener('dragend', handleDragEnd);
        
        // Add new handlers
        node.addEventListener('dragstart', handleDragStart);
        node.addEventListener('dragend', handleDragEnd);
        
        // Initialize the scope action containers inside the screen scope
        const actionsContainer = node.querySelector('.scope-actions-container');
        if (actionsContainer) {
            // Ensure event listeners are set up
            const existingDragover = actionsContainer._dragoverSet;
            
            if (!existingDragover) {
                // Flag to prevent duplicate handlers
                actionsContainer._dragoverSet = true;
                
                actionsContainer.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    actionsContainer.classList.add('drag-over');
                    
                    // Hide the placeholder when dragging over empty container
                    const placeholder = actionsContainer.parentElement.querySelector('.canvas-placeholder');
                    if (placeholder) {
                        placeholder.style.visibility = 'hidden';
                    }
                });
                
                actionsContainer.addEventListener('dragleave', (e) => {
                    if (!e.currentTarget.contains(e.relatedTarget)) {
                        actionsContainer.classList.remove('drag-over');
                        
                        // Show the placeholder again if container is empty
                        if (actionsContainer.children.length === 0) {
                            const placeholder = actionsContainer.parentElement.querySelector('.canvas-placeholder');
                            if (placeholder) {
                                placeholder.style.visibility = '';
                            }
                        }
                    }
                });
            }
        }
    });
    
    // Reinitialize action nodes
    const actionNodes = document.querySelectorAll('.action-node:not(.screen-scope-node)');
    actionNodes.forEach(node => {
        node.draggable = true;
        
        // Remove existing handlers to avoid duplicates
        node.removeEventListener('dragstart', handleActionDragStart);
        node.removeEventListener('dragend', handleActionDragEnd);
        
        // Add new handlers
        node.addEventListener('dragstart', handleActionDragStart);
        node.addEventListener('dragend', handleActionDragEnd);
    });
    
    // Ensure action items are draggable
    setupActionItemsDraggable();
    
    // Update placeholder visibility
    updatePlaceholderVisibility();
}

// Function to update the visibility of placeholder elements based on container content
function updatePlaceholderVisibility() {
    console.log('Updating placeholder visibility');
    const scopeContainers = document.querySelectorAll('.scope-actions-container');
    scopeContainers.forEach(container => {
        const placeholder = container.parentElement?.querySelector('.canvas-placeholder');
        if (placeholder) {
            if (container.children.length > 0) {
                // Hide placeholder for non-empty containers
                placeholder.style.display = 'none';
                container.parentElement.querySelector('.scope-placeholder-wrapper').style.display = 'none';
            } else {
                // Show placeholder for empty containers
                placeholder.style.display = '';
                container.parentElement.querySelector('.scope-placeholder-wrapper').style.display = '';
                // Reset opacity in case it was changed during drag
                placeholder.style.opacity = '1';
            }
        } else {
            console.warn('Placeholder not found for container:', container);
        }
    });
}

// Call reinitializeDragAndDrop after loading a script
document.getElementById('scriptSelect')?.addEventListener('change', () => {
    // Wait for DOM updates to complete
    setTimeout(reinitializeDragAndDrop, 500);
});

// Create a container for toast notifications
function createToastContainer() {
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
        
        // Add toast styles
        const style = document.createElement('style');
        style.textContent = `
            .toast-container {
                z-index: 9999;
            }
            .toast {
                min-width: 250px;
                margin-bottom: 10px;
                background-color: white;
                color: #333;
                border-radius: 4px;
                padding: 16px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                transition: all 0.3s ease;
                opacity: 0;
                transform: translateY(-20px);
            }
            .toast.show {
                opacity: 1;
                transform: translateY(0);
            }
            .toast.success {
                border-left: 4px solid #28a745;
            }
            .toast.error {
                border-left: 4px solid #dc3545;
            }
            .toast.info {
                border-left: 4px solid #17a2b8;
            }
            .toast-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }
            .toast-title {
                font-weight: bold;
                margin: 0;
            }
            .toast-message {
                margin: 0;
            }
            .toast-close {
                background: none;
                border: none;
                font-size: 16px;
                cursor: pointer;
                color: #6c757d;
            }
        `;
        document.head.appendChild(style);
    }
}

// Function to show a toast notification
function showToast(message, type = 'success', duration = 3000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        createToastContainer();
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // Create toast content
    const toastHeader = document.createElement('div');
    toastHeader.className = 'toast-header';
    
    const toastTitle = document.createElement('p');
    toastTitle.className = 'toast-title';
    toastTitle.textContent = type.charAt(0).toUpperCase() + type.slice(1);
    
    const closeButton = document.createElement('button');
    closeButton.className = 'toast-close';
    closeButton.innerHTML = '&times;';
    closeButton.onclick = () => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    };
    
    toastHeader.appendChild(toastTitle);
    toastHeader.appendChild(closeButton);
    
    const toastMessage = document.createElement('p');
    toastMessage.className = 'toast-message';
    toastMessage.textContent = message;
    
    // Assemble toast
    toast.appendChild(toastHeader);
    toast.appendChild(toastMessage);
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Show toast with animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto-remove after duration
    if (duration) {
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
    
    return toast;
}

// Helper function to handle drops on action containers
function dropActionOnContainer(e, container) {
    console.log('Processing drop on container:', container.className);
    
    // Clear indicators
    document.querySelectorAll('.drop-indicator').forEach(el => el.remove());
    container.classList.remove('drag-over');
    
    // Find the dragging element
    const draggingNode = document.querySelector('.dragging');
    if (!draggingNode) {
        console.log('No dragging node found');
        return;
    }
    
    // Don't allow screen scopes to be dropped into action containers
    if (draggingNode.classList.contains('screen-scope-node')) {
        console.log('Cannot drop screen scope into action container');
        return;
    }
    
    // Get the data transfer
    const dragDataStr = e.dataTransfer.getData('application/json');
    const plainData = e.dataTransfer.getData('text/plain');
    console.log('Drop data (plain):', plainData);
    console.log('Drop data (json):', dragDataStr);
    
    let dragData = null;
    try {
        if (dragDataStr) {
            dragData = JSON.parse(dragDataStr);
        }
    } catch (error) {
        console.error('Failed to parse drag data:', error);
    }
    
    // Check if we're creating a new node or moving an existing one
    const isFromSidebar = document.querySelector('.dragging-from-sidebar') || 
                          (dragData && dragData.fromSidebar);
    
    if (isFromSidebar) {
        // Create a new action node
        const actionId = dragData ? dragData.actionId : plainData;
        const action = actions[actionId];
        
        if (!action) {
            console.error('Action not found:', actionId);
            return;
        }
        
        console.log('Creating new action node:', actionId);
        const node = createActionNode(actionId, action);
        
        // Add any properties from drag data
        if (dragData && dragData.properties && dragData.properties !== '{}') {
            node.dataset.properties = dragData.properties;
            updateNodeDisplay(node);
        }
        
        // Insert at the correct position
        const afterElement = getActionDragAfterElement(container, e.clientY);
        if (afterElement) {
            container.insertBefore(node, afterElement);
        } else {
            container.appendChild(node);
        }
    } 
    // Otherwise if we're just moving an existing node
    else if (draggingNode.classList.contains('action-node')) {
        console.log("Moving existing action node");
        
        // Don't allow dragging between different scope types without explicit approval
        const sourceIsScope = draggingNode.closest('.screen-scope-node') !== null;
        const targetIsScope = container.closest('.screen-scope-node') !== null;
        
        if ((sourceIsScope && !targetIsScope) || (!sourceIsScope && targetIsScope)) {
            console.log('Moving between different container types');
        }
        
        // Get the position to insert
        const afterElement = getActionDragAfterElement(container, e.clientY);
        
        // Move the node to the new position
        if (afterElement) {
            console.log("Inserting action before:", afterElement.dataset.actionId || 'unknown');
            container.insertBefore(draggingNode, afterElement);
        } else {
            console.log("Appending action to container");
            container.appendChild(draggingNode);
        }
    }
    
    // Reset dragging state
    document.querySelectorAll('.dragging').forEach(el => el.classList.remove('dragging'));
    document.querySelectorAll('.dragging-from-sidebar').forEach(el => el.classList.remove('dragging-from-sidebar'));
    
    // Update visuals and save
    updatePlaceholderVisibility();
    updateAllOrderNumbers();
} 