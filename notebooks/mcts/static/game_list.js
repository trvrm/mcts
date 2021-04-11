
Ractive.components.GameList = Ractive.extend({
    css:`
    .table.is-scrollable tbody {
      overflow-y: scroll;
      max-height:20em;
    }

    `,
    template:`
    
 
<button class="button is-info is-small is-outlined is-rounded" on-click="ws.send('new_game','tictactoe')">
    Play TicTacToe
</button>
 
    

<button class="button is-info is-small is-outlined is-rounded" on-click="ws.send('new_game','connect4')">
   Play Connect4
</button>

   
       
`
});
    