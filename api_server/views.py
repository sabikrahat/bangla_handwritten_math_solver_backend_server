

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


# Create your views here.
@api_view(['GET', 'POST'])
def check(request):
    response_data = {'status': True,
                     'message': 'Connected Successfully...!', 'data': None, }
    if request.method == 'GET':
        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def equation_solve(request):
    if request.method == 'GET':
        response_data = {
            'status': True, 'message': 'Equation Solve Function executed without any data...!', 'data': None, }
        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        print("::::::::::::::::::::::::::", request.data)
        try:
            img_equ = request.data['img_equ']
            print(":::::::: Equation ::::::::", img_equ)
            img_ans = request.data['img_ans']
            print(":::::::: Answer ::::::::", img_ans)

            res = get_equation_and_solve(img_equ, img_ans)

            response_data = {"success": True,
                             "message": "Successfully solved the equation",
                             "result": res}

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            response_data = {"success": False,
                             "message": "Data not found",
                             "result": None}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


def get_equation_and_solve(img_equ, img_ans):
    print(":::::::: Equation ::::::::", img_equ)
    print(":::::::: Answer ::::::::", img_ans)
    return 'Image Found. Message from Backend django server....!'
