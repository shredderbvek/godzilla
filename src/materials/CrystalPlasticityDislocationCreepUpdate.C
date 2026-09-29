#include "CrystalPlasticityDislocationCreepUpdate.h"
#include "libmesh/int_range.h"
#include <algorithm>
#include <cmath>

registerMooseObject("godzillaApp", CrystalPlasticityDislocationCreepUpdate);

InputParameters
CrystalPlasticityDislocationCreepUpdate::validParams()
{
  InputParameters params = CrystalPlasticityStressUpdateBase::validParams();
  params.addRequiredParam<MooseEnum>("mechanism", MooseEnum("glide climb"), "Creep mechanism");
  params.addParam<Real>("gamma0", 1.44e-3, "Reference shear rate (s^-1)");
  params.addParam<Real>("activation_energy", 5.148e-19, "Activation energy (J)");
  params.addParam<Real>("temperature", 1223.15, "Absolute temperature (K)");
  params.addParam<Real>("tau0", 268.2, "Athermal glide stress (MPa)");
  params.addParam<Real>("mu", 77820.0, "Shear modulus at temperature (MPa)");
  params.addParam<Real>("mu0", 265330.0, "Zero-K shear modulus (MPa)");
  params.addParam<Real>("p", 0.181, "Glide barrier exponent p");
  params.addParam<Real>("q", 1.633, "Glide barrier exponent q");
  params.addParam<Real>("s0", 143.41, "Initial glide resistance (MPa)");
  params.addParam<Real>("sbar", 18.03, "Solute drag resistance (MPa)");
  params.addParam<Real>("hs", 397.73, "Glide resistance hardening");
  params.addParam<Real>("dd", 5073.62, "Dynamic recovery coefficient");
  params.addParam<Real>("hb", 104.31, "Glide backstress hardening");
  params.addParam<Real>("h2", 0.015, "Static recovery rate (s^-1)");
  params.addParam<Real>("gamma_threshold", 1e-6, "Static recovery threshold (s^-1)");
  params.addParam<Real>("muprime0", 31130.0, "Local zero-K modulus (MPa)");
  params.addParam<Real>("f", 0.36, "Backstress coupling");
  params.addParam<Real>("tau0c", 7.75e-3, "Climb stress scale (MPa)");
  params.addParam<Real>("pc", 3.0, "Climb exponent");
  params.addParam<Real>("hc", 32.0, "Climb backstress rate");
  params.addParam<Real>("binf", 4.7, "Climb backstress saturation (MPa)");
  params.addParam<Real>("psi", 0.7853981633974483, "Dislocation line character angle (rad)");
  params.addClassDescription("IN 617 thermally activated dislocation glide or climb update.");
  return params;
}

CrystalPlasticityDislocationCreepUpdate::CrystalPlasticityDislocationCreepUpdate(
    const InputParameters & p)
  : CrystalPlasticityStressUpdateBase(p),
    _climb(getParam<MooseEnum>("mechanism") == "climb"),
    _gamma0(getParam<Real>("gamma0")), _activation(getParam<Real>("activation_energy")),
    _temperature(getParam<Real>("temperature")), _tau0(getParam<Real>("tau0")),
    _mu(getParam<Real>("mu")), _mu0(getParam<Real>("mu0")), _p(getParam<Real>("p")),
    _q(getParam<Real>("q")), _s0(getParam<Real>("s0")), _sbar(getParam<Real>("sbar")),
    _hs(getParam<Real>("hs")), _dd(getParam<Real>("dd")), _hb(getParam<Real>("hb")),
    _h2(getParam<Real>("h2")), _gth(getParam<Real>("gamma_threshold")),
    _muprime(getParam<Real>("muprime0")), _f(getParam<Real>("f")),
    _tau0c(getParam<Real>("tau0c")), _pc(getParam<Real>("pc")), _hc(getParam<Real>("hc")),
    _binf(getParam<Real>("binf")), _psi(getParam<Real>("psi")),
    _crysrot(getMaterialProperty<RankTwoTensor>("crysrot")),
    _backstress(declareProperty<std::vector<Real>>(_base_name + "backstress")),
    _backstress_old(getMaterialPropertyOld<std::vector<Real>>(_base_name + "backstress")),
    _previous_b(_number_slip_systems), _previous_s(_number_slip_systems),
    _before_b(_number_slip_systems), _before_s(_number_slip_systems)
{
}

void
CrystalPlasticityDislocationCreepUpdate::initQpStatefulProperties()
{
  CrystalPlasticityStressUpdateBase::initQpStatefulProperties();
  for (const auto i : make_range(_number_slip_systems))
  {
    _slip_resistance[_qp][i] = _s0;
    _backstress[_qp].resize(_number_slip_systems, 0.0);
    _slip_increment[_qp][i] = 0.0;
  }
}

void
CrystalPlasticityDislocationCreepUpdate::setInitialConstitutiveVariableValues()
{
  _slip_resistance[_qp] = _slip_resistance_old[_qp];
  _backstress[_qp] = _backstress_old[_qp];
  _previous_s = _slip_resistance_old[_qp];
  _previous_b = _backstress_old[_qp];
  if (_climb)
    for (const auto i : make_range(_number_slip_systems))
    {
      RealVectorValue m(0.0, 0.0, 0.0), n(0.0, 0.0, 0.0);
      for (unsigned int a = 0; a < 3; ++a)
        for (unsigned int b = 0; b < 3; ++b)
        {
          m(a) += _crysrot[_qp](a, b) * _slip_direction[i](b);
          n(a) += _crysrot[_qp](a, b) * _slip_plane_normal[i](b);
        }
      const auto mxn = m.cross(n);
      RankTwoTensor k;
      k.zero();
      for (unsigned int a = 0; a < 3; ++a)
        for (unsigned int b = 0; b < 3; ++b)
          k(a,b) = m(a) * (std::cos(_psi) * mxn(b) + std::sin(_psi) * m(b));
      const Real tr = k.trace() / 3.0;
      for (unsigned int a = 0; a < 3; ++a) k(a,a) -= tr;
      _flow_direction[_qp][i] = k;
    }
}

void CrystalPlasticityDislocationCreepUpdate::setSubstepConstitutiveVariableValues()
{ _slip_resistance[_qp] = _previous_s; _backstress[_qp] = _previous_b; }
void CrystalPlasticityDislocationCreepUpdate::updateSubstepConstitutiveVariableValues()
{ _previous_s = _slip_resistance[_qp]; _previous_b = _backstress[_qp]; }
void CrystalPlasticityDislocationCreepUpdate::cacheStateVariablesBeforeUpdate()
{ _before_s = _slip_resistance[_qp]; _before_b = _backstress[_qp]; }

bool
CrystalPlasticityDislocationCreepUpdate::calculateSlipRate()
{
  const Real A = _activation / (1.380649e-23 * _temperature);
  for (const auto i : make_range(_number_slip_systems))
  {
    const Real eta = _tau[_qp][i] - _backstress[_qp][i];
    if (_climb)
      _slip_increment[_qp][i] = _gamma0 * std::exp(-A) *
          std::pow(std::abs(eta) / _tau0c, _pc) * (eta < 0.0 ? -1.0 : 1.0);
    else
    {
      const Real x = (std::abs(eta) - _slip_resistance[_qp][i] * _mu / _mu0) * _mu0 / (_tau0 * _mu);
      const Real c = 0.001, r = c * std::tan(3.0 * std::acos(-1.0) / 8.0);
      const Real bracket = x > c / std::sqrt(2.0) ? x : (x < -c ? 0.0 : r - std::sqrt(std::max(0.0, r*r-(x+c)*(x+c))));
      const Real g = std::exp(-A * std::pow(std::max(0.0, 1.0-std::pow(std::min(1.0,bracket),_p)),_q));
      _slip_increment[_qp][i] = _gamma0 * g * (eta < 0.0 ? -1.0 : 1.0);
    }
    if (std::abs(_slip_increment[_qp][i]) * _substep_dt > _slip_incr_tol)
      return false;
  }
  return true;
}

void
CrystalPlasticityDislocationCreepUpdate::calculateConstitutiveSlipDerivative(std::vector<Real> & d)
{
  const Real A = _activation / (1.380649e-23 * _temperature);
  for (const auto i : make_range(_number_slip_systems))
  {
    const Real eta = _tau[_qp][i] - _backstress[_qp][i];
    if (_climb)
      d[i] = _gamma0 * std::exp(-A) * _pc / _tau0c *
             std::pow(std::abs(eta) / _tau0c, _pc - 1.0);
    else
    {
      const Real x = (std::abs(eta) - _slip_resistance[_qp][i] * _mu / _mu0) * _mu0 / (_tau0 * _mu);
      const Real c = 0.001, r = c * std::tan(3.0 * std::acos(-1.0) / 8.0);
      const Real b = x > c / std::sqrt(2.0) ? x : (x < -c ? 0.0 : r - std::sqrt(std::max(0.0, r*r-(x+c)*(x+c))));
      const Real db = x > c / std::sqrt(2.0) ? 1.0 : (x < -c ? 0.0 : (x+c)/std::sqrt(std::max(1e-30, r*r-(x+c)*(x+c))));
      if (b <= 0.0 || b >= 1.0) d[i] = 0.0;
      else d[i] = std::abs(_slip_increment[_qp][i]) * A * _p * _q *
          std::pow(b,_p-1.0) * std::pow(1.0-std::pow(b,_p),_q-1.0) * db * _mu0 / (_tau0*_mu);
    }
  }
}

bool
CrystalPlasticityDislocationCreepUpdate::updateStateVariables()
{
  Real total_glide_rate = 0.0;
  if (!_climb)
    for (const auto i : make_range(_number_slip_systems))
      total_glide_rate += std::abs(_slip_increment[_qp][i]);
  const bool recover = !_climb && total_glide_rate < _gth;

  for (const auto i : make_range(_number_slip_systems))
  {
    if (_climb)
      _backstress[_qp][i] = (_previous_b[i] + _hc * _binf * _slip_increment[_qp][i] * _substep_dt) /
                            (1.0 + _hc * std::abs(_slip_increment[_qp][i]) * _substep_dt);
    else
    {
      const Real rate = std::abs(_slip_increment[_qp][i]);
      const Real recovery = recover ? _h2 : 0.0;
      _slip_resistance[_qp][i] =
          (_previous_s[i] + _substep_dt * ((_hs + _dd * _sbar) * rate + recovery * _s0)) /
          (1.0 + _substep_dt * (_dd * rate + recovery));
      const Real D = _hb * _mu0 / _slip_resistance[_qp][i] / (_muprime/_f - _mu);
      _backstress[_qp][i] = (_previous_b[i] + _hb * _slip_increment[_qp][i] * _substep_dt) /
                             (1.0 + D * std::abs(_slip_increment[_qp][i]) * _substep_dt);
      if (_slip_resistance[_qp][i] < 0.0) return false;
    }
  }
  return true;
}

bool
CrystalPlasticityDislocationCreepUpdate::areConstitutiveStateVariablesConverged()
{
  return isConstitutiveStateVariableConverged(_backstress[_qp], _before_b, _previous_b, _rel_state_var_tol) &&
         (_climb || isConstitutiveStateVariableConverged(_slip_resistance[_qp], _before_s, _previous_s, _resistance_tol));
}
