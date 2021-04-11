const MainScreen = Ractive.extend({
  css:`
  @media screen and (max-width: 768px) {
  .section {
    padding:0;
  }
}
  `,
  template:`
    <NavBar readyState={{readyState}} user={{user}}/>
    
    <section class="section">
        <div class="container is-fluid">
            
            <div class="columns">
                <div class="column is-one-third">
                    <Notifications notifications={{notifications}} />
                    
                    <GameList games={{games}} ws={{ws}}/>
                    <hr>
                    <pre style="display:none">{{JSON.stringify(.,null,2)}}</pre>
                </div>
                <div class="column">
                    {{#if current_game}}
                        <br>
                        <div class="has-text-centered">
                        
                            <h4>
                                {{#if current_game.result=="PLAYER1"}}
                                    You win!
                                {{/if}}
                                {{#if current_game.result=="PLAYER2"}}
                                    You lose!
                                {{/if}}
                                {{#if current_game.result=="DRAW"}}
                                    Draw
                                {{/if}}
                                {{#if current_game.result=="INPROGRESS"}}
                                    {{#if current_game.player=="ONE"}}
                                    Your turn
                                    {{else}}
                                    Thinking...
                                    {{/if}}
                                {{/if}}
                            </h4>
                        
                            {{#if current_game.name=="tictactoe"}}
                                <TicTacToeBoard 
                                    ws={{ws}}
                                    game={{current_game}} 
                                />
                            
                            {{elseif current_game.name=="connect4"}}
                                <Connect4Board 
                                    ws={{ws}}
                                    game={{current_game}} 
                                />
                            {{/if}}
                            
                        </div>
                    {{/if}}
                </div>
            </div>
        </div>
    </section>
    
  `,
  
  oninit() {
    const protocol = (location.protocol==="http:") ? 'ws' : 'wss';
    const url      = `${protocol}://${location.host}/ws`;
    
    
    
    const ws       = new ReconnectingWebSocket(url, null, {debug: true, reconnectInterval: 3000});
    this.set('ws',ws);
    const stateChange = () => {
        this.set('readyState', ws.readyState);
    };

    // might tighten this up even more
    // maybe [name, arg1, arg2]
    // e.g. ['set',path, value]
    // or   ['push',path,value]
    const handlers= {
        set:(keypath,value)=>{
            this.set(keypath,value);
        },
        push:(keypath,value)=>{
            this.push(keypath,value);
        }
    };
                
    ws.onmessage = event=> {
        const input = JSON.parse(event.data);
        const name = input[0];
        const args = input.slice(1);
        if (name in handlers)
            return handlers[name](...args);
        else
            console.warn(input);
    };
    
    ws.onopen       = stateChange;
    ws.onclose      = stateChange;
    ws.onerror      = stateChange;
    ws.onconnecting = stateChange;
    stateChange();
  }
});