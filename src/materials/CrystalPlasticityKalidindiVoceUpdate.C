//
// Created by ghostrobot96 on 11/6/26.
//
#include "CrystalPlasticityKalidindiVoceUpdate.h"
#include "libmesh/int_range.h"

registerMooseObject("godzillaApp", CrystalPlasticityKalidindiVoceUpdate);

InputParameters
CrystalPlasticityKalidindiVoceUpdate::validParams()
{
  InputParameters params = CrystalPlasticityKalidindiUpdate::validParams();
  params.addClassDescription("Voce hardening: Saturation strength evolution and anisotropic hardening");
  params.addParam<Real>("gss_sat_initial", 37.8, "initial slip system saturation strength");
  params.addParam<Real>("xm_gss", 5e-4, "saturation strength rate scaling exponent");
  params.addParam<Real>("ao_sat", 5e10, "inital slip system saturation strength");
  params.addParam<Real>("n_gss", 1, "non-linear Voce hardening exponent");
  params.addParam<bool>("is_gss_sat_constant", false, "Checks whether saturation strength is constant");

  return params;
}

CrystalPlasticityKalidindiVoceUpdate::CrystalPlasticityKalidindiVoceUpdate(
  const InputParameters & parameters)
  : CrystalPlasticityKalidindiUpdate(parameters),
    _gss_sat_initial(getParam<Real>("gss_sat_initial")),
    _xm_gss(getParam<Real>("xm_gss")),
    _ao_sat(getParam<Real>("ao_sat")),
    _n_gss(getParam<Real>("n_gss")),
    _is_gss_sat_constant(getParam<bool>("is_gss_sat_constant"))
{
}

void
 CrystalPlasticityKalidindiVoceUpdate::calculateStateVariableEvolutionRateComponent()
{
  Real sum_slip_resistance = 0.;

  for (const auto i : make_range(_number_slip_systems))
  {
    _slip_resistance_increment[i] = 0; // clear out increment from previous iteration
    sum_slip_resistance += std::abs(_slip_increment[_qp][i]);
  }

  Real _gss_sat;
  if (_is_gss_sat_constant == true)
  {
    _gss_sat = _gss_sat_initial;
  }else
  {
    if (sum_slip_resistance > 0.0)
      _gss_sat = _gss_sat_initial * std::pow(sum_slip_resistance / _ao_sat, _xm_gss);
    else
      _gss_sat = _gss_sat_initial;
  }

  for (const auto i : make_range(_number_slip_systems))
  {
    Real weighted_slip_rate = 0;

    Real h_ratio = (_gss_sat - _slip_resistance[_qp][i]) / (_gss_sat - _gss_initial);
    if (_n_gss != 1.0)
      h_ratio = std::pow(std::abs(h_ratio), _n_gss);

    for (const auto j : make_range(_number_slip_systems))
    {
      unsigned int iplane, jplane;
      iplane = i/3;
      jplane = j/3;

      if (iplane == jplane) // self vs latent hardening
      {
        // q^{\alpha \beta} = 1 for self hardening
       weighted_slip_rate += std::abs(_slip_increment[_qp][j]);
      }
      else
      {
        weighted_slip_rate += _r * std::abs(_slip_increment[_qp][j]);
      }
    }
    _slip_resistance_increment[i] = _h * h_ratio * weighted_slip_rate;
  }
}