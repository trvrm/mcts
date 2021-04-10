STATES        =['Connecting','Connected','Closing','Closed']
STATECLASSES  =['is-warning','is-success','is-warning','is-danger']

Ractive.components.NavBar = Ractive.extend({
    data(){
        return {
            states:STATES,
            stateclasses:STATECLASSES
        };
    },
    template:`
      <nav class="navbar  is-fixed-bottom is-info">
        <div class="navbar-brand">
          <div class="navbar-item">
            <span class="tag {{stateclasses[readyState]}}">{{states[readyState]}}</span>
          </div>
          <div class="navbar-item">
            {{user.name}}
          </div>
        </div>
      </nav>
`});