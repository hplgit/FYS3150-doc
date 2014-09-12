// Class to compute the square of a number
template<class T>
class Squared{
  public:
    // Default constructor, not used here
    Squared(){}
    // Overload the function operator()
    T operator()(T x){
      return x*x;}

};

