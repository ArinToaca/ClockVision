import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import './shared-styles.js';
import '@polymer/iron-ajax/iron-ajax.js'

class EmployeesTracking extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles">
        :host {
          display: block;

          padding: 10px;
        }
      </style>

      <template is="dom-repeat" items="{{employees}}">
        <div class="card">
          <h1>[[item.name]]</h1>
          <p>[[item.at_work]]</p>
          <template is="dom-repeat" items="{{employees_history}}">
          <p>[[item.start_work]]</p>
          <p>[[item.end_work]]</p>
          </template>
        </div>
      </template>

      <iron-ajax auto url="http://127.0.0.1:5000/all_workers" method="GET" handle-as="json" on-response="getAllWorkers"></iron-ajax>

    `;
    }

    static get properties() {
      return {
        employees: {
          type: Array,
          value() {
            return [this.employees];
          }
          }
        }
      };
    }

    ready(){
      super.ready();
      console.log("i am ready!");
    }

    getAllWorkers(event, request) {
      const response = request.response;
      this.employees = response;
      
      var myObj = response[0].worker_history;
      console.log(myObj[0]);


      /*var result = {};
for (var i=0; i<response[0].worker_history.length; i++) {
  result[arr[i].key] = response[0].worker_history[i].value;
}
  console.log*/
      //this.employees_history = [{"start_work": 150, "end_work":100}, {"start_work": 10000, "end_work":1005}];
    }

  
}

window.customElements.define('my-emt', EmployeesTracking);
