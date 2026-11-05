#include "CrystalPlasticityBussoOrowanIrradiationUpdate.h"
#include "libmesh/int_range.h"
#include <cmath>
#include <algorithm>

registerMooseObject("SolidMechanicsApp", CrystalPlasticityBussoOrowanIrradiationUpdate);

InputParameters
CrystalPlasticityBussoOrowanIrradiationUpdate::validParams()
{
  InputParameters params = CrystalPlasticityStressUpdateBase::validParams();
  params.addClassDescription("Busso-Orowan Crystal Plasticity constitutive model with irradiation loop hardening");
  params.addParam<Real>("ao", 1.0e7, "Reference slip rate coefficient (1/s)");
  params.addParam<Real>("p", 0.5, "Flow rule exponent p");
  params.addParam<Real>("q", 1.0, "Flow rule exponent q");
  params.addParam<Real>("activation", 5.0e-16, "Activation energy Q0 (0.001 J)");
  params.addParam<Real>("k", 1.38e-20, "Boltzmann constant k (0.001 J/K)");
  params.addParam<Real>("T", 573.0, "Temperature in Kelvin (e.g. 300 C = 573 K)");
  params.addParam<Real>("tau_not", 390.0, "Reference mechanical threshold stress tau_0 (MPa)");
  params.addParam<Real>("G", 75581.0, "Elastic shear modulus at T (MPa)");
  params.addParam<Real>("G_not", 88000.0, "Elastic shear modulus at 0K (MPa)");
  params.addParam<Real>("q_rho", 0.09, "Dislocation statistical factor");
  params.addParam<Real>("q_d", 0.55, "Loop defect strength factor");
  params.addParam<Real>("A", 3.1e13, "Loop density scaling factor (1/mm^3)");
  params.addParam<Real>("B", 6.25e-6, "Loop diameter scaling factor (mm)");
  params.addParam<Real>("b", 2.54e-7, "Burgers vector magnitude (mm)");
  params.addParam<Real>("k_mul", 0.06, "Dislocation proliferation rate");
  params.addParam<Real>("l_d", 1.0e-5, "Average mobile dislocation length (mm)");
  params.addParam<Real>("R_c", 1.5e-6, "Critical annihilation radius (mm)");
  params.addParam<Real>("k_dyn", 100.0, "Dynamic recovery coefficient");
  params.addParam<Real>("c", 0.9, "Loop annihilation exponent");
  params.addParam<Real>("lambda", 1.5e-6, "Dislocation mean free path (mm)");
  params.addParam<Real>("gss_initial", 60.8, "Initial slip resistance (MPa)");
  params.addParam<Real>("dpa", 2.85, "Irradiation dose (dpa)");
  params.addParam<Real>("dislocation_density_mobile_initial", 1.3e7, "Initial mobile dislocation density (1/mm^2)");
  params.addParam<Real>("dislocation_density_immobile_initial", 1.3e7, "Initial immobile dislocation density (1/mm^2)");
  params.addParam<Real>("r", 0.03, "Latent hardening interaction coefficient");
  params.addParam<Real>("dislocation_density_mobile_tol", 1e-6, "Convergence tolerance for mobile dislocation density");
  params.addParam<Real>("dislocation_density_immobile_tol", 1e-6, "Convergence tolerance for immobile dislocation density");
  params.addParam<Real>("loop_density_tol", 1e-6, "Convergence tolerance for loop density");
  params.addDeprecatedParam<Real>("slip_incr_tol", "slip_increment_tolerance", "Allowable slip increment tolerance");

  return params;
}

CrystalPlasticityBussoOrowanIrradiationUpdate::CrystalPlasticityBussoOrowanIrradiationUpdate(
  const InputParameters & parameters)
  : CrystalPlasticityStressUpdateBase(parameters),
    _dislocation_density_mobile_tol(getParam<Real>("dislocation_density_mobile_tol")),
    _dislocation_density_immobile_tol(getParam<Real>("dislocation_density_immobile_tol")),
    _loop_density_tol(getParam<Real>("loop_density_tol")),
    _dislocation_density_mobile(declareProperty<std::vector<Real>>(_base_name + "mobile_dislocation_density")),
    _dislocation_density_mobile_old(getMaterialPropertyOld<std::vector<Real>>(_base_name + "mobile_dislocation_density")),
    _dislocation_density_immobile(declareProperty<std::vector<Real>>(_base_name + "immobile_dislocation_density")),
    _dislocation_density_immobile_old(getMaterialPropertyOld<std::vector<Real>>(_base_name + "immobile_dislocation_density")),
    _loop_density(declareProperty<std::vector<Real>>(_base_name + "loop_density")),
    _loop_density_old(getMaterialPropertyOld<std::vector<Real>>(_base_name + "loop_density")),
    _ao(getParam<Real>("ao")),
    _p(getParam<Real>("p")),
    _q(getParam<Real>("q")),
    _activation(getParam<Real>("activation")),
    _k(getParam<Real>("k")),
    _T(getParam<Real>("T")),
    _tau_not(getParam<Real>("tau_not")),
    _G(getParam<Real>("G")),
    _G_not(getParam<Real>("G_not")),
    _gss_initial(getParam<Real>("gss_initial")),
    _q_rho(getParam<Real>("q_rho")),
    _q_d(getParam<Real>("q_d")),
    _A(getParam<Real>("A")),
    _B(getParam<Real>("B")),
    _b(getParam<Real>("b")),
    _k_mul(getParam<Real>("k_mul")),
    _l_d(getParam<Real>("l_d")),
    _R_c(getParam<Real>("R_c")),
    _k_dyn(getParam<Real>("k_dyn")),
    _c(getParam<Real>("c")),
    _lambda(getParam<Real>("lambda")),
    _dpa(getParam<Real>("dpa")),
    _dislocation_density_mobile_initial(getParam<Real>("dislocation_density_mobile_initial")),
    _dislocation_density_immobile_initial(getParam<Real>("dislocation_density_immobile_initial")),
    _r(getParam<Real>("r")),
    _slip_resistance_increment(_number_slip_systems, 0.0),
    _dislocation_density_mobile_increment(_number_slip_systems, 0.0),
    _dislocation_density_immobile_increment(_number_slip_systems, 0.0),
    _loop_density_increment(_number_slip_systems, 0.0),
    _previous_substep_slip_resistance(_number_slip_systems, 0.0),
    _previous_substep_dislocation_density_mobile(_number_slip_systems, 0.0),
    _previous_substep_dislocation_density_immobile(_number_slip_systems, 0.0),
    _previous_substep_loop_density(_number_slip_systems, 0.0),
    _slip_resistance_before_update(_number_slip_systems, 0.0),
    _dislocation_density_mobile_before_update(_number_slip_systems, 0.0),
    _dislocation_density_immobile_before_update(_number_slip_systems, 0.0),
    _loop_density_before_update(_number_slip_systems, 0.0)
{
}

void
CrystalPlasticityBussoOrowanIrradiationUpdate::initQpStatefulProperties()
{
  CrystalPlasticityStressUpdateBase::initQpStatefulProperties();

  _dislocation_density_mobile[_qp].resize(_number_slip_systems);
  _dislocation_density_immobile[_qp].resize(_number_slip_systems);
  _loop_density[_qp].resize(_number_slip_systems);

  const Real initial_loop_density = (_dpa > 0.0) ? _A * std::sqrt(_dpa) : 0.0;
  const Real d_loop = (_dpa > 0.0) ? _B * std::sqrt(_dpa) : 0.0;

  for (const auto i : make_range(_number_slip_systems))
  {
    _slip_increment[_qp][i] = 0.0;
    _dislocation_density_mobile[_qp][i] = _dislocation_density_mobile_initial;
    _dislocation_density_immobile[_qp][i] = _dislocation_density_immobile_initial;
    _loop_density[_qp][i] = initial_loop_density;
  }

  calculateSlipResistance();
}

void
CrystalPlasticityBussoOrowanIrradiationUpdate::calculateSlipResistance()
{
  const Real d_loop = (_dpa > 0.0) ? _B * std::sqrt(_dpa) : 0.0;

  for (const auto i : make_range(_number_slip_systems))
  {
    Real sum_rho = 0.0;
    for (const auto j : make_range(_number_slip_systems))
    {
      const Real q_ab = (i == j) ? 1.0 : _r;
      sum_rho += q_ab * (_dislocation_density_mobile[_qp][j] + _dislocation_density_immobile[_qp][j]);
    }
    const Real rad = _q_rho * sum_rho + _q_d * _loop_density[_qp][i] * d_loop;
    _slip_resistance[_qp][i] = _G * _b * std::sqrt(std::max<Real>(rad, 0.0));
  }
}

void
CrystalPlasticityBussoOrowanIrradiationUpdate::setInitialConstitutiveVariableValues()
{
  CrystalPlasticityStressUpdateBase::setInitialConstitutiveVariableValues();
  _slip_resistance[_qp] = _slip_resistance_old[_qp];
  _dislocation_density_mobile[_qp] = _dislocation_density_mobile_old[_qp];
  _dislocation_density_immobile[_qp] = _dislocation_density_immobile_old[_qp];
  _loop_density[_qp] = _loop_density_old[_qp];

  _previous_substep_slip_resistance = _slip_resistance_old[_qp];
  _previous_substep_dislocation_density_mobile = _dislocation_density_mobile_old[_qp];
  _previous_substep_dislocation_density_immobile = _dislocation_density_immobile_old[_qp];
  _previous_substep_loop_density = _loop_density_old[_qp];
}

void
CrystalPlasticityBussoOrowanIrradiationUpdate::setSubstepConstitutiveVariableValues()
{
  CrystalPlasticityStressUpdateBase::setSubstepConstitutiveVariableValues();
  _slip_resistance[_qp] = _previous_substep_slip_resistance;
  _dislocation_density_mobile[_qp] = _previous_substep_dislocation_density_mobile;
  _dislocation_density_immobile[_qp] = _previous_substep_dislocation_density_immobile;
  _loop_density[_qp] = _previous_substep_loop_density;
}

void
CrystalPlasticityBussoOrowanIrradiationUpdate::updateSubstepConstitutiveVariableValues()
{
  CrystalPlasticityStressUpdateBase::updateSubstepConstitutiveVariableValues();
  _previous_substep_slip_resistance = _slip_resistance[_qp];
  _previous_substep_dislocation_density_mobile = _dislocation_density_mobile[_qp];
  _previous_substep_dislocation_density_immobile = _dislocation_density_immobile[_qp];
  _previous_substep_loop_density = _loop_density[_qp];
}

bool
CrystalPlasticityBussoOrowanIrradiationUpdate::calculateSlipRate()
{
  const Real threshold = _tau_not * _G / _G_not;
  const Real aggregate_coeff = _activation / (_k * _T);

  for (const auto i : make_range(_number_slip_systems))
  {
    const Real abs_tau = std::abs(_tau[_qp][i]);
    const Real g = _slip_resistance[_qp][i];

    if (abs_tau <= g)
    {
      _slip_increment[_qp][i] = 0.0;
    }
    else
    {
      const Real effectiveStress = abs_tau - g;
      const Real stress_ratio = effectiveStress / threshold;

      // Barrier term: 1 - (tau_eff / tau_hat)^p, clamped to zero if stress exceeds threshold
      Real barrier = 0.0;
      if (stress_ratio < 1.0)
        barrier = 1.0 - std::pow(stress_ratio, _p);

      Real slip_rate = _ao * std::exp(-aggregate_coeff * std::pow(barrier, _q));
      if (_tau[_qp][i] < 0.0)
        slip_rate = -slip_rate;

      _slip_increment[_qp][i] = slip_rate;
    }

    if (std::abs(_slip_increment[_qp][i]) * _substep_dt > _slip_incr_tol)
    {
      if (_print_convergence_message)
        mooseWarning("Maximum allowable slip increment exceeded: ",
                     std::abs(_slip_increment[_qp][i]) * _substep_dt);
      return false;
    }
  }
  return true;
}

void
CrystalPlasticityBussoOrowanIrradiationUpdate::calculateEquivalentSlipIncrement(
    RankTwoTensor & equivalent_slip_increment)
{
  CrystalPlasticityStressUpdateBase::calculateEquivalentSlipIncrement(equivalent_slip_increment);
}

void
CrystalPlasticityBussoOrowanIrradiationUpdate::calculateConstitutiveSlipDerivative(std::vector<Real> & dslip_dtau)
{
  const Real threshold = _tau_not * _G / _G_not;
  const Real aggregate_coeff = _activation / (_k * _T);

  for (const auto i : make_range(_number_slip_systems))
  {
    const Real abs_tau = std::abs(_tau[_qp][i]);
    const Real g = _slip_resistance[_qp][i];

    if (abs_tau <= g)
    {
      dslip_dtau[i] = 0.0;
    }
    else
    {
      const Real effectiveStress = abs_tau - g;
      const Real stress_ratio = effectiveStress / threshold;

      if (stress_ratio >= 1.0)
      {
        dslip_dtau[i] = 0.0;
      }
      else
      {
        // Numerical guard against 0^(p-1) singularity as stress_ratio -> 0
        const Real u_safe = std::max<Real>(stress_ratio, 1.0e-12);
        const Real barrier = 1.0 - std::pow(u_safe, _p);
        const Real barrier_safe = std::max<Real>(barrier, 1.0e-12);

        const Real prefactor = (aggregate_coeff * _p * _q * _ao) / threshold;
        const Real exp_term = std::exp(-aggregate_coeff * std::pow(barrier_safe, _q));

        dslip_dtau[i] = prefactor * exp_term *
                        std::pow(barrier_safe, _q - 1.0) *
                        std::pow(u_safe, _p - 1.0);
      }
    }
  }
}

void
CrystalPlasticityBussoOrowanIrradiationUpdate::cacheStateVariablesBeforeUpdate()
{
  CrystalPlasticityStressUpdateBase::cacheStateVariablesBeforeUpdate();
  _slip_resistance_before_update = _slip_resistance[_qp];
  _dislocation_density_mobile_before_update = _dislocation_density_mobile[_qp];
  _dislocation_density_immobile_before_update = _dislocation_density_immobile[_qp];
  _loop_density_before_update = _loop_density[_qp];
}

void
CrystalPlasticityBussoOrowanIrradiationUpdate::calculateStateVariableEvolutionRateComponent()
{
  const Real d_loop = (_dpa > 0.0) ? _B * std::sqrt(_dpa) : 0.0;
  const Real R_ann  = 0.5 * d_loop;

  for (const auto i : make_range(_number_slip_systems))
  {
    const Real delta_gamma = std::abs(_substep_dt * _slip_increment[_qp][i]);

    // 1. Mobile dislocation density evolution (Eq. 11)
    const Real rho_m_prev = _previous_substep_dislocation_density_mobile[i];
    const Real num_mobile = rho_m_prev + ((_k_mul / _l_d - 1.0 / _lambda) / _b) * delta_gamma;
    const Real den_mobile = 1.0 + (2.0 * _R_c / _b) * delta_gamma;
    _dislocation_density_mobile[_qp][i] = std::max<Real>(num_mobile / den_mobile, 0.0);

    // 2. Immobile dislocation density evolution (Eq. 11)
    const Real rho_i_prev = _previous_substep_dislocation_density_immobile[i];
    const Real num_immobile = rho_i_prev + (delta_gamma / (_b * _lambda));
    const Real den_immobile = 1.0 + _k_dyn * delta_gamma;
    _dislocation_density_immobile[_qp][i] = std::max<Real>(num_immobile / den_immobile, 0.0);

    // 3. Interstitial loop density evolution via Newton-Raphson (Eq. 14)
    const Real N_prev = _previous_substep_loop_density[i];
    if (N_prev > 0.0 && d_loop > 0.0 && delta_gamma > 0.0)
    {
      const Real rho_m_curr = _dislocation_density_mobile[_qp][i];
      const Real X = (R_ann / (_b * d_loop)) * std::pow(d_loop, _c) *
                     std::pow(std::max<Real>(rho_m_curr, 1.0e-20), 1.0 - _c) * delta_gamma;

      Real N = N_prev;
      const Real tol = 1.0e-8 * N_prev;
      const unsigned int max_iter = 25;

      for (unsigned int iter = 0; iter < max_iter; ++iter)
      {
        const Real N_safe = std::max<Real>(N, 1.0e-20);
        const Real N_pow_c = std::pow(N_safe, _c);
        const Real N_pow_c_minus_1 = std::pow(N_safe, _c - 1.0);

        const Real R = X * N_pow_c + N - N_prev;
        const Real J = 1.0 + _c * X * N_pow_c_minus_1;
        const Real delta_N = -R / J;

        N += delta_N;
        N = std::clamp<Real>(N, 0.0, N_prev);

        if (std::abs(delta_N) <= tol || std::abs(R) <= tol)
          break;
      }
      _loop_density[_qp][i] = N;
    }
    else
    {
      _loop_density[_qp][i] = N_prev;
    }
  }

  // 4. Update Slip Resistance g^alpha (Eq. 10)
  calculateSlipResistance();
  for (const auto i : make_range(_number_slip_systems))
    _slip_resistance_increment[i] = _slip_resistance[_qp][i] - _previous_substep_slip_resistance[i];
}

bool
CrystalPlasticityBussoOrowanIrradiationUpdate::updateStateVariables()
{
  for (const auto i : make_range(_number_slip_systems))
  {
    if (_slip_resistance[_qp][i] < 0.0 ||
        _dislocation_density_mobile[_qp][i] < 0.0 ||
        _dislocation_density_immobile[_qp][i] < 0.0 ||
        _loop_density[_qp][i] < 0.0)
      return false;
  }
  return true;
}

bool
CrystalPlasticityBussoOrowanIrradiationUpdate::areConstitutiveStateVariablesConverged()
{
  return isConstitutiveStateVariableConverged(_slip_resistance[_qp],
                                              _slip_resistance_before_update,
                                              _previous_substep_slip_resistance,
                                              _resistance_tol) &&
         isConstitutiveStateVariableConverged(_dislocation_density_mobile[_qp],
                                              _dislocation_density_mobile_before_update,
                                              _previous_substep_dislocation_density_mobile,
                                              _dislocation_density_mobile_tol) &&
         isConstitutiveStateVariableConverged(_dislocation_density_immobile[_qp],
                                              _dislocation_density_immobile_before_update,
                                              _previous_substep_dislocation_density_immobile,
                                              _dislocation_density_immobile_tol) &&
         isConstitutiveStateVariableConverged(_loop_density[_qp],
                                              _loop_density_before_update,
                                              _previous_substep_loop_density,
                                              _loop_density_tol);
}