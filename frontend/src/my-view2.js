/**
 * @license
 * Copyright (c) 2016 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at http://polymer.github.io/PATENTS.txt
 */

import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import './shared-styles.js';
import '@polymer/iron-ajax/iron-ajax.js';
import '@polymer/paper-card/paper-card.js';
import '@vaadin/vaadin-icons/vaadin-icons.js';
import '@polymer/iron-flex-layout/iron-flex-layout.js';

class MyView2 extends PolymerElement {
  static get template() {
    return html`
      
	<style include="shared-styles iron-flex iron-flex-alignment">
        :host {
          display: block;
          padding: 10px;
        }
        .icon-dim {
          --iron-icon-height: 15px;
          --iron-icon-width: 15px;
        }
        .on {
          --iron-icon-fill-color: #4CAF50;
          padding-left: 10px;
        }
        .off {
          --iron-icon-fill-color: #FF5722;
          padding-left: 10px;
        }
        
        paper-card {
          width: 100%;
        }
        p {
          padding-left: 10px;
          color: #484848;
          font-size: 18px;
        }
        a {
          color: #484848;
        }
        iron-icon {
          color: #4285f4;
        }
      .customImg {
        width: 50px;
        height: 50px;
        border-radius: 50%; 
        float: left;
    }
    .flex-horizontal {
      @apply --layout-horizontal;
    }
    .flexchild {
      @apply --layout-flex;
    }
    </style>
     <iron-ajax auto url="http://localhost:5000/all_workers" method="GET" handle-as="json" on-response="getAllWorkers"></iron-ajax>
      
      <template is="dom-repeat" items="{{employees}}">
        <paper-card animatedShadow="true">
          <paper-icon-item class="card-header">
          <p><iron-icon icon="vaadin:circle" class$="{{item.at_work}} icon-dim"></iron-icon> [[item.name]]<img src="http://localhost:5000/static/[[item.worker_id]].jpg" class="customImg"></p>
          <span>&nbsp</span>
          <paper-item-body>
            <template is="dom-repeat" items="[[item.worker_history]]">
            <div>
              <p><iron-icon icon="vaadin:calendar"></iron-icon> [[item.start_work]] <iron-icon icon="vaadin:arrows-long-h"></iron-icon>
              [[item.end_work]] <iron-icon icon="vaadin:clock"></iron-icon>  [[item.hours_worked]]</p>
            </div>
            </template>
          </paper-item-body>
        </paper-card>
        <span>&nbsp</span>
      </template>
    `;
    }
    static get properties() {
      return {
        employees: {
          type: Array,
          value() { return [this.employees]}
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
    }
  }

window.customElements.define('my-view2', MyView2);
