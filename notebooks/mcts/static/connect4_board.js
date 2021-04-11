/*
    I want a mechanism for highlighting legal moves.
    
    This means 2 things: SENDING the legal moves with the board state.
    Painting them in response to mouse activity.
    
    Maybe we have a clickable overlay when it's your turn?
    
    
*/
Ractive.components.Connect4Board = Ractive.extend({
    
    css:`
        .board{
            fill:#0000ff;
        }
        
        .square.black{
            fill:#000000;
        }
        .slot.O{
            fill:red;
        }
        .slot.X{
            fill:yellow;
        }
        
        .target.ONE:hover{
            
                fill:red;
        }
         
    `,    
 
    template:`  
        
        <svg width="350" height="350" class="default">
        
        
            {{#if (game.result=="INPROGRESS")}}
            
                <rect class="board drop" width="350" height="40">
                
                </rect>
                
                {{#each game.board[0] as cell:i}}
                    <g transform="translate({{i*50}},0)">
                      <rect x="5" y="5" width="40" height="30" rx="5" 
                        class="target {{game.player}}"
                        on-click="ws.send("connect4_move",i)"
                      />
     
                    </g>
                {{/each}}
            {{/if}}
            
            <rect class="board" y="50" width="350" height="300">
            </rect>
            
            
            
            {{#each game.board as row:j}}
                {{#each row as cell:i}}
                    <g transform="translate({{i*50}},{{50+j*50}})">
                      <circle cx="25" cy="25" r="20" stroke="black" stroke-width="3" class="slot {{cell}}"
                        
                      />
                    </g>
                {{/each}}
            {{/each}}
        </svg>
     
    ` 
});