#include "godzillaApp.h"
#include "Moose.h"
#include "AppFactory.h"
#include "ModulesApp.h"
#include "MooseSyntax.h"

InputParameters
godzillaApp::validParams()
{
  InputParameters params = MooseApp::validParams();
  params.set<bool>("use_legacy_material_output") = false;
  params.set<bool>("use_legacy_initial_residual_evaluation_behavior") = false;
  return params;
}

godzillaApp::godzillaApp(const InputParameters & parameters) : MooseApp(parameters)
{
  godzillaApp::registerAll(_factory, _action_factory, _syntax);
}

godzillaApp::~godzillaApp() {}

void
godzillaApp::registerAll(Factory & f, ActionFactory & af, Syntax & syntax)
{
  ModulesApp::registerAllObjects<godzillaApp>(f, af, syntax);
  Registry::registerObjectsTo(f, {"godzillaApp"});
  Registry::registerActionsTo(af, {"godzillaApp"});

  /* register custom execute flags, action syntax, etc. here */
}

void
godzillaApp::registerApps()
{
  registerApp(godzillaApp);
}

/***************************************************************************************************
 *********************** Dynamic Library Entry Points - DO NOT MODIFY ******************************
 **************************************************************************************************/
extern "C" void
godzillaApp__registerAll(Factory & f, ActionFactory & af, Syntax & s)
{
  godzillaApp::registerAll(f, af, s);
}
extern "C" void
godzillaApp__registerApps()
{
  godzillaApp::registerApps();
}
