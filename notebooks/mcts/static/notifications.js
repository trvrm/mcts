
Ractive.components.Notifications = Ractive.extend({
    data(){
        return {messages:[]};
    },
        
    template:`
        {{#each notifications as notification:index}}
            <div class="notification is-{{notification.level}}">
                <button class="delete"
                    on-click='@this.splice('notifications',index,1)'
                    > </button>
                {{notification.text}}
                
            </div>
         {{/each}}
`
});
    