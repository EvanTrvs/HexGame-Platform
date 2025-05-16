class HexBoard {
    // Configuration constants
    static CONFIG = {
        // Spacing configuration
        SPACING: {
            HORIZONTAL_MULTIPLIER: 1,    // Controls horizontal spacing between cells
            VERTICAL_MULTIPLIER: 0.8,      // Controls vertical spacing between cells
            OFFSET_MULTIPLIER: 0,       // Controls vertical offset for odd columns
            CELL_MARGIN: 2,                // Additional margin between cells
        },
        // Sizing configuration
        SIZING: {
            MIN_CELL_SIZE: 20,             // Minimum cell size in pixels
            MAX_CELL_SIZE: 60,             // Maximum cell size in pixels
            BASE_CELL_SIZE: 40,            // Default cell size
            HORIZONTAL_PADDING: 180,        // Horizontal padding around the board
            VERTICAL_PADDING: 30,          // Vertical padding around the board
        },
        // Responsive configuration
        RESPONSIVE: {
            SMALL_SCREEN_BREAKPOINT: 768,  // Breakpoint for small screens
            SMALL_SCREEN_MULTIPLIER: 0.8,  // Size multiplier for small screens
        }
    };

    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.boardSize = 0;  // Initialize to 0, will be set when first board state is received
        this.cellSize = HexBoard.CONFIG.SIZING.BASE_CELL_SIZE;
        this.cells = [];
        this.boardState = null;
        this.cellClickCallback = null;  // Store the click callback
    }

    /**
     * Calculate the appropriate cell size based on container dimensions
     */
    calculateCellSize() {
        const containerWidth = this.container.parentElement.clientWidth;
        const containerHeight = this.container.parentElement.clientHeight;
        
        // Calculate base size
        const baseSize = Math.min(
            containerWidth / (this.boardSize * (HexBoard.CONFIG.SPACING.HORIZONTAL_MULTIPLIER/2)),
            containerHeight / (this.boardSize * (HexBoard.CONFIG.SPACING.VERTICAL_MULTIPLIER/2))
        );
        
        // Apply responsive adjustments for small screens
        const isSmallScreen = window.innerWidth <= HexBoard.CONFIG.RESPONSIVE.SMALL_SCREEN_BREAKPOINT;
        const responsiveMultiplier = isSmallScreen ? HexBoard.CONFIG.RESPONSIVE.SMALL_SCREEN_MULTIPLIER : 1;
        
        // Calculate final size with constraints
        return Math.max(
            HexBoard.CONFIG.SIZING.MIN_CELL_SIZE,
            Math.min(
                HexBoard.CONFIG.SIZING.MAX_CELL_SIZE,
                baseSize * responsiveMultiplier
            )
        );
    }

    /**
     * Clear all cells from the board
     */
    clearBoard() {
        while (this.container.firstChild) {
            this.container.removeChild(this.container.firstChild);
        }
        this.cells = [];
    }

    /**
     * Initialize the hexagonal board
     */
    initialize() {
        this.container.style.position = 'relative';
        this.container.style.transform = 'rotate(0deg)';
        this.container.style.transformOrigin = 'center';
        this.container.style.padding = `${HexBoard.CONFIG.SIZING.VERTICAL_PADDING}px ${HexBoard.CONFIG.SIZING.HORIZONTAL_PADDING}px`;
        
        // Calculate initial cell size
        this.cellSize = this.calculateCellSize();
        
        // Set container size
        this.updateContainerSize();
        
        // Create the hexagonal grid
        this.createHexGrid();
    }

    /**
     * Create the hexagonal grid
     */
    createHexGrid() {
        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                const cell = this.createHexCell(row, col);
                this.cells.push(cell);
                this.container.appendChild(cell);
            }
        }
        
        // Reattach click handlers if a callback exists
        if (this.cellClickCallback) {
            this.setCellClickCallback(this.cellClickCallback);
        }
    }

    /**
     * Update container size based on current configuration
     */
    updateContainerSize() {
        this.container.style.width = `${this.boardSize * this.cellSize * HexBoard.CONFIG.SPACING.HORIZONTAL_MULTIPLIER}px`;
        this.container.style.height = `${this.boardSize * this.cellSize * HexBoard.CONFIG.SPACING.VERTICAL_MULTIPLIER}px`;
    }

    /**
     * Create a single hexagonal cell
     */
    createHexCell(row, col) {
        const cell = document.createElement('div');
        cell.className = 'hex-cell';
        cell.dataset.row = row;
        cell.dataset.col = col;

        // Calculate position using configuration
        const x = col * this.cellSize * HexBoard.CONFIG.SPACING.HORIZONTAL_MULTIPLIER + (this.boardSize * 13.33 + 183) + row*-30;
        const y = row * this.cellSize * HexBoard.CONFIG.SPACING.VERTICAL_MULTIPLIER + 
                 (col % 2) * this.cellSize * HexBoard.CONFIG.SPACING.OFFSET_MULTIPLIER + 10;

        cell.style.position = 'absolute';
        cell.style.left = `${x}px`;
        cell.style.top = `${y}px`;
        cell.style.width = `${this.cellSize}px`;
        cell.style.height = `${this.cellSize}px`;
        cell.style.margin = `${HexBoard.CONFIG.SPACING.CELL_MARGIN}px`;
        cell.style.clipPath = 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)';

        return cell;
    }

    /**
     * Update the board state
     */
    updateBoard(boardState) {
        if (!boardState) return;

        // Check if board size has changed
        const newBoardSize = boardState.length;
        if (newBoardSize !== this.boardSize) {
            this.boardSize = newBoardSize;
            this.clearBoard();
            this.initialize();
        }

        this.boardState = boardState;
        this.updateCellColors();
    }

    /**
     * Update the colors of all cells based on the board state
     */
    updateCellColors() {
        if (!this.boardState) return;

        this.cells.forEach(cell => {
            const row = parseInt(cell.dataset.row);
            const col = parseInt(cell.dataset.col);
            const value = this.boardState[row][col];

            // Reset cell style
            cell.style.backgroundColor = '#ffffff';

            // Set color based on value
            if (value === 1) { // Blue player
                cell.style.backgroundColor = '#2196F3';
            } else if (value === 2) { // Red player
                cell.style.backgroundColor = '#f44336';
            }
        });
    }

    /**
     * Set the callback for cell clicks
     */
    setCellClickCallback(callback) {
        this.cellClickCallback = callback;  // Store the callback
        this.cells.forEach(cell => {
            // Remove any existing click listeners
            cell.removeEventListener('click', this._handleCellClick);
            // Add the new click listener
            cell.addEventListener('click', this._handleCellClick);
        });
    }

    /**
     * Handle cell click event
     */
    _handleCellClick = (event) => {
        const cell = event.currentTarget;
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        if (this.cellClickCallback) {
            this.cellClickCallback(row, col);
        }
    }

    /**
     * Resize the board based on container size
     */
    resize() {
        // Calculate new cell size
        this.cellSize = this.calculateCellSize();
        
        // Update container size
        this.updateContainerSize();
        
        // Update all cells
        this.cells.forEach(cell => {
            const row = parseInt(cell.dataset.row);
            const col = parseInt(cell.dataset.col);
            
            const x = col * this.cellSize * HexBoard.CONFIG.SPACING.HORIZONTAL_MULTIPLIER + (this.boardSize * 13.33 + 183) + row*-30;
            const y = row * this.cellSize * HexBoard.CONFIG.SPACING.VERTICAL_MULTIPLIER + 
                     (col % 2) * this.cellSize * HexBoard.CONFIG.SPACING.OFFSET_MULTIPLIER + 10;
            
            cell.style.left = `${x}px`;
            cell.style.top = `${y}px`;
            cell.style.width = `${this.cellSize}px`;
            cell.style.height = `${this.cellSize}px`;
        });
    }
}

// Export the class for use in other files
window.HexBoard = HexBoard; 