import { PolymerElement, html } from '@polymer/polymer/polymer-element.js';
import './shared-styles.js';

class Dashboard extends PolymerElement {
  static get template() {
    return html`
      <style include="shared-styles">
        :host {
          display: block;

          padding: 10px;
        }
      </style>

    `;
  }
}

window.customElements.define('my-dashboard', Dashboard);
