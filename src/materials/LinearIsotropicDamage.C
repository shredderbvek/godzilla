#include "LinearIsotropicDamage.h"

// Replaced by tools/install_into_app.py -- this is intentionally not a valid app label.
registerMooseObject("godzillaApp", LinearIsotropicDamage);

InputParameters
LinearIsotropicDamage::validParams()
{
  InputParameters params = ComputeStressBase::validParams();
  params.addClassDescription("Demonstration small-strain isotropic elasticity with a stateful strain-norm damage law");
  params.addRequiredRangeCheckedParam<Real>("youngs_modulus", "youngs_modulus > 0", "Young's modulus");
  params.addRequiredRangeCheckedParam<Real>("poissons_ratio", "poissons_ratio > -1 & poissons_ratio < 0.5", "Poisson's ratio");
  params.addRangeCheckedParam<Real>("damage_threshold", 0.01, "damage_threshold >= 0", "Strain-norm activation threshold");
  params.addRangeCheckedParam<Real>("damage_coefficient", 0.05, "damage_coefficient >= 0", "Strain-norm damage multiplier per step");
  params.addRangeCheckedParam<Real>("maximum_damage", 0.99, "maximum_damage > 0 & maximum_damage < 1", "Maximum damage");
  return params;
}

LinearIsotropicDamage::LinearIsotropicDamage(const InputParameters & parameters)
  : ComputeStressBase(parameters),
    _E(getParam<Real>("youngs_modulus")),
    _nu(getParam<Real>("poissons_ratio")),
    _threshold(getParam<Real>("damage_threshold")),
    _coefficient(getParam<Real>("damage_coefficient")),
    _max_damage(getParam<Real>("maximum_damage")),
    _damage(declareProperty<Real>(_base_name + "damage")),
    _damage_old(getMaterialPropertyOld<Real>(_base_name + "damage"))
{
}

void
LinearIsotropicDamage::initQpStatefulProperties()
{
  ComputeStressBase::initQpStatefulProperties();
  _damage[_qp] = 0.0;
}

void
LinearIsotropicDamage::computeQpStress()
{
  const RankTwoTensor & eps = _mechanical_strain[_qp];
  const Real norm = eps.L2norm();
  Real d = _damage_old[_qp];
  bool active = false;
  if (norm > _threshold && d < _max_damage)
  {
    d += _coefficient * norm;
    if (d >= _max_damage)
      d = _max_damage;
    else
      active = true;
  }
  _damage[_qp] = d;

  RankFourTensor C;
  C.fillSymmetricIsotropicEandNu(_E, _nu);
  const RankTwoTensor sigma0 = C * eps;
  _stress[_qp] = (1.0 - d) * sigma0;
  _elastic_strain[_qp] = eps;
  _Jacobian_mult[_qp] = (1.0 - d) * C;
  if (active && norm > 0.0)
  {
    const RankTwoTensor dd_deps = (_coefficient / norm) * eps;
    for (unsigned int i = 0; i < 3; ++i)
      for (unsigned int j = 0; j < 3; ++j)
        for (unsigned int k = 0; k < 3; ++k)
          for (unsigned int l = 0; l < 3; ++l)
            _Jacobian_mult[_qp](i, j, k, l) -= sigma0(i, j) * dd_deps(k, l);
  }
}
