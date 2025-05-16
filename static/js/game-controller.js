class GameController {
    constructor() {
        this.board = new HexBoard('hex-board');
        this.pollingInterval = null;
        
        // Initialize board
        this.board.initialize();
        this.board.setCellClickCallback(this.handleCellClick.bind(this));
        
        // Initialize event listeners
        this.initializeEventListeners();
        
        // Start polling for updates
        this.startPolling();

        this.bluePlayerName = 'Blue Player';
        this.redPlayerName = 'Red Player';

        // Initialize board size selection
        this.initializeBoardSizeSelection();

        // Initialize replay controls
        this.initializeReplayControls();
    }

    /**
     * Start polling for game state updates
     */
    startPolling() {
        // Poll every 500ms
        this.pollingInterval = setInterval(() => {
            this.updateGameState();
        }, 500);
    }

    /**
     * Stop polling for updates
     */
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Start game button
        document.getElementById('start-game').addEventListener('click', () => {
            this.startGame();
        });

        // Pause game button
        document.getElementById('pause-game').addEventListener('click', () => {
            this.pauseGame();
        });

        // Resume game button
        document.getElementById('resume-game').addEventListener('click', () => {
            this.resumeGame();
        });

        // Resign game button
        document.getElementById('resign-game').addEventListener('click', () => {
            this.resignGame();
        });

        // Save game button
        document.getElementById('save-game').addEventListener('click', () => {
            this.showSaveModal();
        });

        // Save modal form
        document.getElementById('save-game-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveGame();
        });

        // Save modal cancel button
        document.querySelector('.cancel-button').addEventListener('click', () => {
            this.hideSaveModal();
        });

        // Window resize handler
        window.addEventListener('resize', () => {
            this.board.resize();
        });

        // Stop polling when page is hidden
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopPolling();
            } else {
                this.startPolling();
            }
        });
    }

    /**
     * Show the save game modal
     */
    showSaveModal() {
        const modal = document.getElementById('save-modal');
        modal.style.display = 'block';
    }

    /**
     * Hide the save game modal
     */
    hideSaveModal() {
        const modal = document.getElementById('save-modal');
        modal.style.display = 'none';
    }

    /**
     * Initialize board size selection
     */
    initializeBoardSizeSelection() {
        const startButton = document.getElementById('start-game');
        const boardSizeModal = document.getElementById('board-size-modal');
        const confirmButton = document.getElementById('confirm-board-size');
        const cancelButton = document.getElementById('cancel-board-size');

        startButton.addEventListener('click', () => {
            boardSizeModal.style.display = 'block';
        });

        confirmButton.addEventListener('click', async () => {
            const boardSize = parseInt(document.getElementById('board-size').value);
            boardSizeModal.style.display = 'none';
            await this.startGame(boardSize);
        });

        cancelButton.addEventListener('click', () => {
            boardSizeModal.style.display = 'none';
        });

        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            if (event.target === boardSizeModal) {
                boardSizeModal.style.display = 'none';
            }
        });
    }

    /**
     * Start a new game
     */
    async startGame(boardSize) {
        try {
            const response = await fetch('/api/game/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    board_size: boardSize
                })
            });

            if (!response.ok) {
                throw new Error('Failed to start game');
            }

            const data = await response.json();
            this.updateGameState(data);
        } catch (error) {
            console.error('Error starting game:', error);
        }
    }

    updatePlayerNames() {
        document.querySelector('.blue-player .player-name').textContent = this.bluePlayerName;
        document.querySelector('.red-player .player-name').textContent = this.redPlayerName;
    }

    /**
     * Handle cell click
     */
    async handleCellClick(x, y) {
        try {
            const response = await fetch('/api/game/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    x: x,
                    y: y
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.updateGameState();
            } else {
                console.error('Move failed:', data.message);
            }
        } catch (error) {
            console.error('Error making move:', error);
        }
    }

    /**
     * Pause the game
     */
    async pauseGame() {
        try {
            const response = await fetch('/api/game/pause', {
                method: 'POST'
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.updateGameState();
            } else {
                console.error('Failed to pause game:', data.message);
            }
        } catch (error) {
            console.error('Error pausing game:', error);
        }
    }

    /**
     * Resume the game
     */
    async resumeGame() {
        try {
            const response = await fetch('/api/game/resume', {
                method: 'POST'
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.updateGameState();
            } else {
                console.error('Failed to resume game:', data.message);
            }
        } catch (error) {
            console.error('Error resuming game:', error);
        }
    }

    /**
     * Resign from the game
     */
    async resignGame() {
        try {
            const response = await fetch('/api/game/resign', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    player_color: this.currentPlayerColor
                })
            });

            const result = await response.json();
            if (result.status === 'error') {
                console.error('Failed to resign:', result.message);
                return;
            }
            
            this.updateGameState();
        } catch (error) {
            console.error('Error resigning:', error);
        }
    }

    /**
     * Save the current game
     */
    async saveGame() {
        const bluePlayerName = document.getElementById('blue-player-name').value;
        const redPlayerName = document.getElementById('red-player-name').value;

        try {
            const response = await fetch('/api/game/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    blue_player_name: bluePlayerName,
                    red_player_name: redPlayerName
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.hideSaveModal();
                alert('Game saved successfully!');
            } else {
                console.error('Failed to save game:', data.message);
                alert('Failed to save game: ' + data.message);
            }
        } catch (error) {
            console.error('Error saving game:', error);
            alert('Error saving game: ' + error.message);
        }
    }

    /**
     * Update the game state from the server
     */
    async updateGameState() {
        try {
            const response = await fetch('/api/game/state');
            const result = await response.json();
            
            if (result.status === 'error') {
                console.error('Error getting game state:', result.message);
                return;
            }
            
            this.updateGameStateDisplay(result.data);
        } catch (error) {
            console.error('Error updating game state:', error);
        }
    }

    /**
     * Update the game state display with detailed information
     */
    updateGameStateDisplay(data) {
        if (!data) {
            console.error('No data received for game state update');
            return;
        }

        const gameStateElement = document.getElementById('game-state');
        const gameMessageElement = document.getElementById('game-message');

        // Update game state
        if (data.game_state) {
            const message = data.game_state.message;
            gameStateElement.textContent = message;
        }

        // Update message info
        if (data.action_message) {
            gameMessageElement.textContent = data.action_message;
        }

        // Update board state
        if (data.board_state) {
            this.board.updateBoard(data.board_state);
        }

        // Update current player
        if (data.current_player) {
            this.updateCurrentPlayer(data.current_player);
        }

        // Update player names
        if (data.players) {
            this.updatePlayerNames(data.players);
        }

        // Update button states based on game state
        if (data.game_state) {
            this.updateButtonStates(data.game_state.state);
        }
    }

    updateCurrentPlayer(playerName) {
        if (!playerName) return;
        
        const bluePlayer = document.querySelector('.blue-player');
        const redPlayer = document.querySelector('.red-player');
        
        // Remove current player class from both
        bluePlayer.classList.remove('current-player');
        redPlayer.classList.remove('current-player');
        
        // Add current player class to the active player
        if (playerName === this.bluePlayerName) {
            bluePlayer.classList.add('current-player');
        } else if (playerName === this.redPlayerName) {
            redPlayer.classList.add('current-player');
        }
    }

    updatePlayerNames(players) {
        if (!players) return;
        
        // Extract player names from the response
        const blueName = players.blue.replace('Blue Player Name: ', '');
        const redName = players.red.replace('Red Player Name: ', '');
        
        // Update the player name elements
        const bluePlayerElement = document.querySelector('.blue-player .player-name');
        const redPlayerElement = document.querySelector('.red-player .player-name');
        
        bluePlayerElement.textContent = blueName || 'Blue Player';
        redPlayerElement.textContent = redName || 'Red Player';
        
        // Store the clean names for comparison
        this.bluePlayerName = blueName;
        this.redPlayerName = redName;
    }

    /**
     * Update the game info panel with end game details
     */
    updateGameInfoPanel(gameState) {
        const winnerElement = document.getElementById('game-winner');
        const endReasonElement = document.getElementById('game-end-reason');
        
        if (gameState.winner) {
            winnerElement.textContent = `Winner: ${gameState.winner}`;
            winnerElement.className = `winner ${gameState.winner.toLowerCase()}`;
        } else {
            winnerElement.textContent = 'No winner';
            winnerElement.className = 'winner';
        }
        
        if (gameState.end_reason) {
            endReasonElement.textContent = `End Reason: ${gameState.end_reason}`;
        } else {
            endReasonElement.textContent = '';
        }
    }

    /**
     * Initialize replay controls
     */
    initializeReplayControls() {
        const prevButton = document.getElementById('prev-move');
        const nextButton = document.getElementById('next-move');

        prevButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/game/prev-move', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                if (response.ok) {
                    this.updateGameState();
                }
            } catch (error) {
                console.error('Error moving to previous move:', error);
            }
        });

        nextButton.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/game/next-move', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                if (response.ok) {
                    this.updateGameState();
                }
            } catch (error) {
                console.error('Error moving to next move:', error);
            }
        });
    }

    /**
     * Update button states based on game state
     */
    updateButtonStates(state) {
        const startButton = document.getElementById('start-game');
        const pauseButton = document.getElementById('pause-game');
        const resumeButton = document.getElementById('resume-game');
        const resignButton = document.getElementById('resign-game');
        const saveButton = document.getElementById('save-game');
        const prevButton = document.getElementById('prev-move');
        const nextButton = document.getElementById('next-move');

        // Reset all buttons
        [startButton, pauseButton, resumeButton, resignButton, saveButton, prevButton, nextButton].forEach(button => {
            button.disabled = true;
        });

        // Mode REPLAY - tous les boutons désactivés sauf navigation
        if (state === 'REPLAY') {
            this.board.setCellClickCallback(null);
            prevButton.disabled = false;
            nextButton.disabled = false;
            return;
        }

        // Réactive les clics sur les cellules si on n'est pas en mode REPLAY
        this.board.setCellClickCallback(this.handleCellClick.bind(this));

        // Enable buttons based on game state
        switch (state) {
            case 'NOT_INITIALIZED':
            case 'NOT_STARTED':
                startButton.disabled = false;
                break;
            case 'ACTIVE':
                pauseButton.disabled = false;
                resignButton.disabled = false;
                saveButton.disabled = false;
                prevButton.disabled = false;
                break;
            case 'PAUSED':
                resumeButton.disabled = false;
                resignButton.disabled = false;
                saveButton.disabled = false;
                prevButton.disabled = false;
                break;
            case 'FINISHED':
                startButton.disabled = false;
                saveButton.disabled = false;
                prevButton.disabled = false;
                break;
            case 'CORRUPTED':
                startButton.disabled = false;
                break;
        }
    }
}

// Initialize the game controller when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.gameController = new GameController();
});

// Add styles for current player highlight
const style = document.createElement('style');
style.textContent = `
    .player.current-player {
        background-color: rgba(0, 0, 0, 0.1);
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
    }
`;
document.head.appendChild(style); 