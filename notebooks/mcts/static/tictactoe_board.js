/*
    I want a mechanism for highlighting legal moves.
    
    This means 2 things: SENDING the legal moves with the board state.
    Painting them in response to mouse activity.
    
    Maybe we have a clickable overlay when it's your turn?
    
    
*/
Ractive.components.TicTacToeBoard = Ractive.extend({
    
    css:`
        .board{
            fill:#741b34;
        }
        
        .square.black{
            fill:#000000;
        }
        
        .square.empty{
            fill:#aaaaaa;
        }
        
        .square.O{
            fill:#ffffff;
            stroke:#000000;
            stroke-width:3; 
        }
        
        .square.X{
            fill:#111111;
            stroke:#000000;
            stroke-width:3; 
        }
        
        .empty.highlighted:hover{
            fill:rgba(240,240,240,0.8);
        }
        .wall{
            fill: #eedab6;
        }
        .wallslot{
            fill: #000000;
        }.
        
        .piece{
            
        }
        .piece.selected{
            stroke:yellow;
            stroke-width:4;
        }
    `,    
 
    template:` aaa
        <h2>Player {{game.player}}</h2>
        <h3>{{game.result}}</h3>
        <svg width="310" height="310" class="default">
            <g class="board">
                
                {{#each game.board as row:j}}
                    {{#each row as cell:i}}
                        <g transform="translate({{i*(300/game.size)}},{{j*300/game.size}})">
                            {{#if (game.player=="ONE") & (game.result=="IN PROGRESS")}}
                                <rect 
                                    on-click="ws.send('play_move',game.name,j, i)"
                                    x="5"  y="5" rx="3" ry="3" width="{{270/game.size}}"  height="{{270/game.size}}" 
                                    class="square   highlighted {{cell}}" >
                                </rect>
                            {{else}}
                                <rect  
                                    x="5"  y="5" rx="3" ry="3" width="{{270/game.size}}"  height="{{270/game.size}}" 
                                    class="square {{cell}}  " >
                                </rect>
                            {{/if}}
                        </g>
                    {{/each}}
                {{/each}} 

            </g>
        </svg>
        
        
    ` 
});