//* This file is part of the MOOSE framework
//* https://mooseframework.inl.gov
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html
#include "godzillaTestApp.h"
#include "godzillaApp.h"
#include "Moose.h"
#include "AppFactory.h"
#include "MooseSyntax.h"

InputParameters
godzillaTestApp::validParams()
{
  InputParameters params = godzillaApp::validParams();
  params.set<bool>("use_legacy_material_output") = false;
  params.set<bool>("use_legacy_initial_residual_evaluation_behavior") = false;
  return params;
}

godzillaTestApp::godzillaTestApp(const InputParameters & parameters) : MooseApp(parameters)
{
  godzillaTestApp::registerAll(
      _factory, _action_factory, _syntax, getParam<bool>("allow_test_objects"));
}

godzillaTestApp::~godzillaTestApp() {}

void
godzillaTestApp::registerAll(Factory & f, ActionFactory & af, Syntax & s, bool use_test_objs)
{
  godzillaApp::registerAll(f, af, s);
  if (use_test_objs)
  {
    Registry::registerObjectsTo(f, {"godzillaTestApp"});
    Registry::registerActionsTo(af, {"godzillaTestApp"});
  }
}

void
godzillaTestApp::registerApps()
{
  registerApp(godzillaApp);
  registerApp(godzillaTestApp);
}

/***************************************************************************************************
 *********************** Dynamic Library Entry Points - DO NOT MODIFY ******************************
 **************************************************************************************************/
// External entry point for dynamic application loading
extern "C" void
godzillaTestApp__registerAll(Factory & f, ActionFactory & af, Syntax & s)
{
  godzillaTestApp::registerAll(f, af, s);
}
extern "C" void
godzillaTestApp__registerApps()
{
  godzillaTestApp::registerApps();
}
