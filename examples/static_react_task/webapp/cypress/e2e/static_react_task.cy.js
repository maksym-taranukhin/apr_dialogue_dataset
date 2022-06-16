describe("Loads static_react_task", () => {
  it("Makes request for agent", () => {
    cy.visit("/");
    cy.intercept({ pathname: "/request_agent" }).as("agentRequest");
    cy.wait("@agentRequest").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });
  it("Loads correct react elements", () => {
    cy.visit("/");
    cy.get('[data-cy="directions-container"]');
    cy.get('[data-cy="task-data-text"]');
    cy.get('[data-cy="good-button"]');
    cy.get('[data-cy="bad-button"]');
  });
});

describe("Submits static_react_task", () => {
  it("Gets request from pressing good button", () => {
    cy.visit("/");
    cy.intercept({ pathname: "/submit_task" }).as("goodTaskSubmit");
    cy.get('[data-cy="good-button"]').click();
    cy.wait("@goodTaskSubmit").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });
  it("Shows alert from pressing good button", () => {
    cy.visit("/");
    const stub = cy.stub();
    cy.on("window:alert", stub);
    cy.get('[data-cy="good-button"]')
      .click()
      .then(() => {
        expect(stub.getCall(0)).to.be.calledWith(
          'The task has been submitted! Data: {"rating":"good"}'
        );
      });
  });

  it("Gets request from pressing bad button", () => {
    cy.visit("/");
    cy.intercept({ pathname: "/submit_task" }).as("badTaskSubmit");
    cy.get('[data-cy="bad-button"]').click();
    cy.wait("@badTaskSubmit").then((interception) => {
      expect(interception.response.statusCode).to.eq(200);
    });
  });

  it("Shows alert from pressing bad button", () => {
    cy.visit("/");
    const stub = cy.stub();
    cy.on("window:alert", stub);
    cy.get('[data-cy="bad-button"]')
      .click()
      .then(() => {
        expect(stub.getCall(0)).to.be.calledWith(
          'The task has been submitted! Data: {"rating":"bad"}'
        );
      });
  });
});
